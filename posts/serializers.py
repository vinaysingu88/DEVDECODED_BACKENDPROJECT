
from rest_framework import serializers
from .models import Posts
from django.db.models import Count, Q


class PostsSerializer(serializers.ModelSerializer):

    author = serializers.ReadOnlyField(source='author.name')
    upvote_count = serializers.SerializerMethodField()
    downvote_count = serializers.SerializerMethodField()

    @staticmethod
    def with_vote_counts(queryset):
        return queryset.annotate(
            upvote_count=Count('votes', filter=Q(votes__vote_type='UP')),
            downvote_count=Count('votes', filter=Q(votes__vote_type='DOWN')),
        )

    def get_upvote_count(self, obj):
        if hasattr(obj, 'upvote_count'):
            return obj.upvote_count
        return obj.votes.filter(vote_type='UP').count()

    def get_downvote_count(self, obj):
        if hasattr(obj, 'downvote_count'):
            return obj.downvote_count
        return obj.votes.filter(vote_type='DOWN').count()

    class Meta:
        model = Posts
        fields = [
            'id',
            'title',
            'content',
            'author',
            'status',
            'created_at',
            'updated_at',
            'upvote_count',
            'downvote_count',
            'share_count',
        ]

        read_only_fields = [
            'id',
            'author',
            'status',
            'created_at',
            'updated_at',
            'upvote_count',
            'downvote_count',
            'share_count',
        ]
