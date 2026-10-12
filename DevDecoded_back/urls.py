
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/posts/', include('posts.urls')),
    path('api/public/posts/', include('posts.public_urls')),
    path('api/admin/users/', include('users.admin_urls')),

]