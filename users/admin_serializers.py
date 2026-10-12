
from rest_framework import serializers
from .models import User


class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'name',
            'email',
            'role',
            'created_at',
        ]
        read_only_fields = fields
