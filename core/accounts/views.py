from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .models import User
from .serializers import UserSerializer, UserRegistrationSerializer, LoginSerializer


class RegisterView(generics.CreateAPIView):
    """API endpoint for user registration."""
    
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Create token for the new user
        token, created = Token.objects.get_or_create(user=user)
        
        # Return user data with token
        user_data = UserSerializer(user).data
        return Response({
            'user': user_data,
            'token': token.key,
            'message': 'Регистрация успешна.'
        }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """API endpoint for user login."""
    serializer = LoginSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data['user']
    
    # Create or get token
    token, created = Token.objects.get_or_create(user=user)
    
    # Note: We don't use login() here because API uses Token authentication, not Session
    # Session login would require CSRF token which is not needed for API
    
    user_data = UserSerializer(user).data
    return Response({
        'user': user_data,
        'token': token.key,
        'message': 'Вход выполнен успешно.'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_view(request):
    """API endpoint to get current authenticated user."""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

