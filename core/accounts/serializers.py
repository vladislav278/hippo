from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model (read operations)."""
    
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    hospital_name = serializers.CharField(source='hospital.name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'role', 'role_display', 'hospital', 'hospital_name', 'is_active', 'date_joined']
        read_only_fields = ['id', 'is_active', 'date_joined']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password_confirm', 'role', 'hospital']
        extra_kwargs = {
            'role': {'required': False},
        }
    
    def validate(self, attrs):
        """Validate that passwords match."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Пароли не совпадают."})
        return attrs
    
    def validate_email(self, value):
        """Validate that email is unique."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует.")
        return value
    
    def validate_hospital(self, value):
        """Validate hospital if provided."""
        if value is None and self.initial_data.get('role') in ['hospital_admin', 'doctor']:
            # Allow None for now, but could add validation here if needed
            pass
        return value
    
    def create(self, validated_data):
        """Create a new user with hashed password."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        # Set default role if not provided
        if 'role' not in validated_data:
            validated_data['role'] = 'doctor'
        
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    
    def validate(self, attrs):
        """Validate user credentials."""
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(request=self.context.get('request'), username=email, password=password)
            if not user:
                raise serializers.ValidationError("Неверный email или пароль.")
            if not user.is_active:
                raise serializers.ValidationError("Аккаунт деактивирован.")
            attrs['user'] = user
        else:
            raise serializers.ValidationError("Необходимо указать email и пароль.")
        
        return attrs

