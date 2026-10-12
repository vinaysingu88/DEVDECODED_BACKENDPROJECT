from django.urls import path
from . import views

urlpatterns = [
    path('', views.public_posts, name='public_posts'),
    path(
        '<int:post_id>/',
        views.public_post_detail,
        name='public_post_detail'
    ),
    path(
        "<int:post_id>/vote/",
        views.vote_post,
        name="vote_post",
    ),
    path(
    "<int:post_id>/share/",
    views.track_post_share,
    name="track_post_share",
),
]
