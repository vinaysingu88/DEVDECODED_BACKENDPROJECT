
from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import User


class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password', 'role']
        read_only_fields = ['id', 'role']

    def create(self, validated_data):
        return User.objects.create_user(
            name=validated_data['name'],
            email=validated_data['email'],
            password=validated_data['password'],
            role='AUTHOR'
        )


class LoginSerializer(serializers.Serializer):

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(
            request=self.context.get('request'),
            email=data['email'],
            password=data['password']
        )

        if user is None:
            raise serializers.ValidationError(
                "Invalid email or password."
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "This account is inactive."
            )

        data['user'] = user
        return data
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "name", "email", "role", "created_at"]
        read_only_fields = ["id", "email", "role", "created_at"]