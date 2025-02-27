from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model, authenticate
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import get_user_model
from django.utils.encoding import force_bytes
from django.utils.encoding import force_str

import random, string, logging

from .serializers import RegisterSerializer, UserSerializer, ForgotPasswordSerializer, ResetPasswordSerializer
from .permissions import IsAdmin, IsTrader
from .tasks import send_email_task

logger = logging.getLogger(__name__)

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        """Set permissions dynamically based on the action."""
        if self.action in ["create", "register", "login"]:
            return [AllowAny()]  
        elif self.action in ["update_profile", "partial_update", "retrieve"]:
            return [IsAuthenticated()]  
        elif self.action == "list":
            return [IsAdmin()]  
        return super().get_permissions()

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def login(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"error": "Please provide both username and password"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": UserSerializer(user).data
            }, status=status.HTTP_200_OK)
        
        return Response(
            {"error": "Invalid credentials"}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def logout(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"error": "Refresh token required"}, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error during logout: {e}")
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["patch"], permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully", "user": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def forget_password(self, request):
        """
        Sends a password reset email with a unique token.
        """
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        user = User.objects.filter(email=email).first()
        if not user:
            logger.warning(f"Password reset attempted for non-existent email: {email}")
            return Response({'error': 'No user found with this email.'}, status=status.HTTP_404_NOT_FOUND)

        # Generate a secure password reset token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Generate the reset link with uid and token
        reset_link = f"{request.scheme}://{request.get_host()}/api/users/reset_password/{uid}/{token}/"

        # Send email with the reset link
        send_email_task(
            'Password Reset Request',
            f"Click the following link to reset your password: {reset_link}",
            [user.email],
        )

        logger.info(f"Password reset email sent to: {email}")
        return Response({'message': 'Password reset email sent.'}, status=status.HTTP_200_OK)

    
    @action(
        detail=False,
        methods=['post'],
        permission_classes=[AllowAny],
        url_path=r'reset_password/(?P<uidb64>[^/]+)/(?P<token>[^/]+)'
    )
    def reset_password(self, request, uidb64, token):
        """
        Resets the user's password using a UID and token from the URL.
        """
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            logger.error(f"Invalid password reset attempt with UID: {uidb64}")
            return Response({'error': 'Invalid token or user ID.'}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            logger.warning(f"Invalid/expired token used for password reset by user: {user.email}")
            return Response({'error': 'Token is invalid or expired.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Generate new password if required
        new_password = serializer.validated_data.get('password')
        if new_password == "GENERATE_RANDOM":
            new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

        user.set_password(new_password)
        user.save()

        # Send the new password to the user (only if generated)
        if "GENERATE_RANDOM" in request.data.values():
            send_email_task(
                'New Password',
                f"Your new password is: {new_password}",
                [user.email],
            )
            logger.info(f"Random password generated and sent to user: {user.email}")
        else:
            logger.info(f"Password reset successful for user: {user.email}")

        return Response({'message': 'Password reset successful.'}, status=status.HTTP_200_OK)
    