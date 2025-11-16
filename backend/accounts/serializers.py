from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения пользователя."""
    
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    hospital_name = serializers.CharField(source='hospital.name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'role', 'role_display', 'hospital', 'hospital_name', 
                  'is_staff', 'is_superuser', 'date_joined']
        read_only_fields = ['id', 'is_staff', 'is_superuser', 'date_joined']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя."""
    
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password_confirm', 'role', 'hospital']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Пароли не совпадают."})
        return attrs
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует.")
        return value
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """Сериализатор для входа."""
    
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise serializers.ValidationError("Неверный email или пароль.")
            
            if not user.check_password(password):
                raise serializers.ValidationError("Неверный email или пароль.")
            
            if not user.is_active:
                raise serializers.ValidationError("Пользователь неактивен.")
            
            attrs['user'] = user
        else:
            raise serializers.ValidationError("Необходимо указать email и пароль.")
        
        return attrs

