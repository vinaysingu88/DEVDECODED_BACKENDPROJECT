from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('admin/users/', views.admin_users, name='admin_users'),
    path(
        'admin/users/<int:user_id>/role/',
        views.update_user_role,
        name='update_user_role'
    ),
    path("me/", views.my_profile, name="my_profile"),
]
