from rest_framework import serializers

from django.contrib.auth import get_user_model


User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(required=False)
    
    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "profile_picture"]

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    profile_picture = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = ["username", "email", "password", "role", "profile_picture"]

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=100)

class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=False, write_only=True)

    def validate(self, data):
        password = data.get('password')
        if not password and password != "GENERATE_RANDOM":
            raise serializers.ValidationError("Password is required or use 'GENERATE_RANDOM' to generate one.")
        return data
