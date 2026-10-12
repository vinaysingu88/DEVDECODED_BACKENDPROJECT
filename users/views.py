
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from users.admin_serializers import AdminUserSerializer

from .serializers import RegisterSerializer, LoginSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import User
from users.permissions import IsAdminRole
from posts.models import Posts
from posts.serializers import PostsSerializer
from .serializers import ProfileSerializer
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()

        return Response({
            'message': 'User registered successfully',
            'user': RegisterSerializer(user).data
        }, status=status.HTTP_201_CREATED)

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(
        data=request.data,
        context={'request': request}
    )

    if serializer.is_valid():
        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)

        return Response({
            'message': 'Login successful',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'role': user.role,
            }
        }, status=status.HTTP_200_OK)

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminRole])
def pending_posts(request):
    posts = Posts.objects.filter(
        status='PENDING'
    ).order_by('-created_at')

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
# GET: List all users (Admin only)
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminRole])
def admin_users(request):
    users = User.objects.all().order_by('-created_at')
    serializer = AdminUserSerializer(users, many=True)
    return Response(serializer.data)


# PUT: Change a user's role (Admin only)
@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdminRole])
def update_user_role(request, user_id):
    user = get_object_or_404(User, id=user_id)

    new_role = request.data.get('role')

    if new_role not in ['ADMIN', 'AUTHOR']:
        return Response(
            {'error': 'Role must be ADMIN or AUTHOR.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Prevent an admin from accidentally demoting their own account
    if user.id == request.user.id and new_role != 'ADMIN':
        return Response(
            {'error': 'You cannot demote your own account.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user.role = new_role
    user.save(update_fields=['role'])

    return Response({
        'message': 'Role updated successfully',
        'userId': user.id,
        'newRole': user.role
    }, status=status.HTTP_200_OK)

@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def my_profile(request):
    user = request.user

    if request.method == "GET":
        serializer = ProfileSerializer(user)
        return Response(serializer.data)

    serializer = ProfileSerializer(
        user,
        data=request.data,
        partial=True,
    )

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=400)