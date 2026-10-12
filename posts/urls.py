
from django.urls import path
from . import views

urlpatterns = [
    path('', views.create_post, name='create_post'),
    path('my-posts/', views.my_posts, name='my_posts'),
    path('<int:post_id>/', views.post_detail, name='post_detail'),
    path('admin/pending/', views.pending_posts, name='pending_posts'),
    path(
        'admin/<int:post_id>/status/',
        views.update_post_status,
        name='update_post_status'
    ),
    path(
        'admin/<int:post_id>/',
        views.admin_delete_post,
        name='admin_delete_post'
    ),
    
]
