
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from .models import Posts, PostVote
from .serializers import PostsSerializer
from django.db.models import F
from users.permissions import IsAdminRole
from rest_framework.permissions import AllowAny
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_post(request):
    serializer = PostsSerializer(data=request.data)

    if serializer.is_valid():
        post = serializer.save(
            author=request.user,
            status='PENDING'
        )

        return Response({
            'message': 'Post created and pending approval',
            'post': PostsSerializer(post).data
        }, status=status.HTTP_201_CREATED)

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_posts(request):
    posts = PostsSerializer.with_vote_counts(
        Posts.objects.filter(author=request.user)
    ).order_by('-created_at')
    serializer = PostsSerializer(posts, many=True)

    return Response(serializer.data)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def post_detail(request, post_id):
    post = get_object_or_404(
        PostsSerializer.with_vote_counts(Posts.objects.all()),
        id=post_id,
    )

    # Authors can access only their own posts.
    # Admins can access any post.
    if request.user.role != 'ADMIN' and post.author_id != request.user.id:
        return Response(
            {'error': 'You do not have permission to access this post.'},
            status=status.HTTP_403_FORBIDDEN
        )

    if request.method == 'GET':
        return Response(PostsSerializer(post).data)

    if request.method == 'PUT':
        serializer = PostsSerializer(post, data=request.data)

        if serializer.is_valid():
            # Authors must get approval again after editing a post.
            if request.user.role == 'ADMIN':
                serializer.save()
            else:
                serializer.save(status='PENDING')

            return Response({
                'message': 'Post updated successfully',
                'post': PostsSerializer(post).data
            })

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    if request.method == 'DELETE':
        post.delete()

        return Response(
            {'message': 'Post deleted successfully'},
            status=status.HTTP_200_OK
        )
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminRole])
def pending_posts(request):
    posts = PostsSerializer.with_vote_counts(Posts.objects.filter(
        status='PENDING'
    )).order_by('-created_at')

    serializer = PostsSerializer(posts, many=True)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdminRole])
def update_post_status(request, post_id):
    post = get_object_or_404(Posts, id=post_id)

    new_status = request.data.get('status')

    if new_status not in ['APPROVED', 'REJECTED']:
        return Response(
            {'error': 'Status must be APPROVED or REJECTED.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    post.status = new_status
    post.save(update_fields=['status', 'updated_at'])

    return Response({
        'message': 'Post status updated',
        'postId': post.id,
        'status': post.status
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminRole])
def admin_delete_post(request, post_id):
    post = get_object_or_404(Posts, id=post_id)
    post.delete()

    return Response(
        {'message': 'Post deleted successfully'},
        status=status.HTTP_200_OK
    )

# View all approved posts
@api_view(['GET'])
@permission_classes([AllowAny])
def public_posts(request):
    posts = PostsSerializer.with_vote_counts(Posts.objects.filter(
        status='APPROVED'
    )).order_by('-created_at')

    search_query = request.query_params.get('search')

    if search_query:
        posts = posts.filter(title__icontains=search_query)

    paginator = PageNumberPagination()
    paginator.page_size = 5

    page = paginator.paginate_queryset(posts, request)
    serializer = PostsSerializer(page, many=True)

    return paginator.get_paginated_response(serializer.data)



# View one approved post
@api_view(['GET'])
@permission_classes([AllowAny])
def public_post_detail(request, post_id):
    post = get_object_or_404(
        PostsSerializer.with_vote_counts(Posts.objects.all()),
        id=post_id,
        status='APPROVED'
    )

    serializer = PostsSerializer(post)
    return Response(serializer.data)


@api_view(["POST", "DELETE"])
@permission_classes([IsAuthenticated])
def vote_post(request, post_id):
    post = get_object_or_404(
        Posts,
        id=post_id,
        status="APPROVED",
    )

    if request.method == "DELETE":
        PostVote.objects.filter(
            post=post,
            user=request.user,
        ).delete()

        return Response({
            "detail": "Vote removed.",
            "upvote_count": post.votes.filter(vote_type=PostVote.UPVOTE).count(),
            "downvote_count": post.votes.filter(vote_type=PostVote.DOWNVOTE).count(),
        })

    vote_type = request.data.get("vote_type")

    if vote_type not in [PostVote.UPVOTE, PostVote.DOWNVOTE]:
        return Response(
            {"detail": "vote_type must be UP or DOWN."},
            status=400,
        )

    vote, created = PostVote.objects.update_or_create(
        post=post,
        user=request.user,
        defaults={"vote_type": vote_type},
    )

    return Response({
        "detail": "Vote recorded.",
        "vote_type": vote.vote_type,
        "created": created,
        "upvote_count": post.votes.filter(vote_type=PostVote.UPVOTE).count(),
        "downvote_count": post.votes.filter(vote_type=PostVote.DOWNVOTE).count(),
    })

@api_view(["POST"])
@permission_classes([AllowAny])
def track_post_share(request, post_id):
    post = get_object_or_404(
        Posts,
        id=post_id,
        status="APPROVED",
    )

    Posts.objects.filter(pk=post.pk).update(
        share_count=F("share_count") + 1
    )

    post.refresh_from_db(fields=["share_count"])

    return Response({
        "detail": "Share recorded.",
        "share_count": post.share_count,
        "upvote_count": post.votes.filter(vote_type=PostVote.UPVOTE).count(),
        "downvote_count": post.votes.filter(vote_type=PostVote.DOWNVOTE).count(),
    })
