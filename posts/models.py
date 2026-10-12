
from django.db import models
from django.conf import settings


class Posts(models.Model):

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    ]

    title = models.CharField(max_length=255)

    content = models.TextField()

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts"
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)
    share_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title
class PostVote(models.Model):
    UPVOTE = "UP"
    DOWNVOTE = "DOWN"

    VOTE_CHOICES = [
        (UPVOTE, "Upvote"),
        (DOWNVOTE, "Downvote"),
    ]

    post = models.ForeignKey(
        "posts.Posts",
        on_delete=models.CASCADE,
        related_name="votes",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="post_votes",
    )
    vote_type = models.CharField(
        max_length=4,
        choices=VOTE_CHOICES,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["post", "user"],
                name="unique_user_vote_per_post",
            )
        ]