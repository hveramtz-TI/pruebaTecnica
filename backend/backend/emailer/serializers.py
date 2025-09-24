from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, Contest, Participant, EmailVerification

class ContestRegistrationSerializer(serializers.ModelSerializer):
    """Serializer para el registro público en el concurso"""
    
    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'phone']
        
    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email ya está registrado.")
        return value
    
    def create(self, validated_data):
        # Crear usuario con username igual al email, sin contraseña inicialmente
        validated_data['username'] = validated_data['email']
        user = CustomUser.objects.create(**validated_data)
        return user

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer para el registro inicial del usuario (admin)"""
    password = serializers.CharField(write_only=True, required=False)
    password_confirm = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'phone', 'password', 'password_confirm']
        
    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email ya está registrado.")
        return value
    
    def validate(self, attrs):
        # En el registro inicial, no se requiere contraseña
        if 'password' in attrs and 'password_confirm' in attrs:
            if attrs['password'] != attrs['password_confirm']:
                raise serializers.ValidationError("Las contraseñas no coinciden.")
            validate_password(attrs['password'])
        return attrs
    
    def create(self, validated_data):
        # Remover password_confirm antes de crear el usuario
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password', None)
        
        # Crear usuario con username igual al email
        validated_data['username'] = validated_data['email']
        user = CustomUser.objects.create(**validated_data)
        
        if password:
            user.set_password(password)
            user.save()
            
        return user

class PasswordCreationSerializer(serializers.Serializer):
    """Serializer para crear contraseña después de verificar email"""
    token = serializers.UUIDField()
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Las contraseñas no coinciden.")
        validate_password(attrs['password'])
        return attrs

class UserLoginSerializer(serializers.Serializer):
    """Serializer para login"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError("Credenciales inválidas.")
            if not user.is_email_verified:
                raise serializers.ValidationError("Debes verificar tu email antes de acceder.")
            attrs['user'] = user
        else:
            raise serializers.ValidationError("Email y contraseña son requeridos.")
        
        return attrs

class UserSerializer(serializers.ModelSerializer):
    """Serializer para mostrar información del usuario"""
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'is_email_verified', 'created_at']
        read_only_fields = ['id', 'email', 'is_email_verified', 'created_at']

class ContestSerializer(serializers.ModelSerializer):
    """Serializer para el concurso"""
    total_participants = serializers.SerializerMethodField()
    
    class Meta:
        model = Contest
        fields = ['id', 'name', 'description', 'start_date', 'end_date', 'is_active', 'winner', 'total_participants', 'created_at']
    
    def get_total_participants(self, obj):
        return obj.participant_set.filter(is_eligible=True).count()

class ParticipantSerializer(serializers.ModelSerializer):
    """Serializer para participantes"""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Participant
        fields = ['id', 'user', 'user_email', 'user_name', 'contest', 'registered_at', 'is_eligible']
        read_only_fields = ['registered_at', 'is_eligible']