from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_users, name='admin_users'),
    path(
        '<int:user_id>/role/',
        views.update_user_role,
        name='update_user_role'
    ),
]