import logging
from typing import TYPE_CHECKING

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .validators import normalize_phone, mask_email
from .utils import get_domain_and_protocol, generate_jwt_response

if TYPE_CHECKING:
    from .models import CustomUser

logger = logging.getLogger(__name__)
User = get_user_model()


class CustomRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ['email', 'phone', 'password', 'password2']
        extra_kwargs = {
            'email': {'required': True},
            'phone': {'required': False},
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует")
        return value.lower().strip()

    def validate_phone(self, value):
        if not value:
            return None
        normalized = normalize_phone(value)
        if not normalized:
            raise serializers.ValidationError(
                "Неверный формат телефона. Используйте формат 8XXXXXXXXXX, +7XXXXXXXXXX или 9XXXXXXXXX"
            )
        if User.objects.filter(phone=normalized).exists():
            raise serializers.ValidationError("Пользователь с таким телефоном уже существует")
        return normalized

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Пароль должен быть не менее 8 символов")
        if value.isdigit():
            raise serializers.ValidationError("Пароль не может состоять только из цифр")
        return value

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password2'):
            raise serializers.ValidationError({"password2": "Пароли не совпадают"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)

        from .tasks import send_verification_email_task
        request = self.context.get('request')
        domain, protocol = get_domain_and_protocol(request)
        send_verification_email_task.delay(user.id, domain, protocol)
        
        logger.info(f"Verification email task queued for {user.email}")
        return user


class LoginSerializer(serializers.Serializer):
    contact = serializers.CharField(required=True)
    contact_type = serializers.ChoiceField(
        choices=['email', 'phone'],
        required=False,
        allow_blank=True  # Разрешить пустую строку
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        contact = attrs.get('contact')
        if not contact:
            raise serializers.ValidationError({
                'contact': 'Это поле обязательно.'
            })
        
        contact = contact.strip()
        contact_type = attrs.get('contact_type') or ''  # Получить значение или пустую строку
        contact_type = contact_type.strip() if contact_type else ''  # Убрать пробелы
        password = attrs.get('password')
        
        if not password:
            raise serializers.ValidationError({
                'password': 'Это поле обязательно.'
            })

        # Автоопределение типа контакта
        if not contact_type or contact_type not in ['email', 'phone']:
            contact_type = 'email' if '@' in contact else 'phone'

        user = self._find_user(contact, contact_type)
        self._validate_password(user, password)
        self._validate_active(user)

        attrs['user'] = user
        return attrs

    def _find_user(self, contact, contact_type):
        """Поиск пользователя по email или телефону"""
        logger.debug(f"Searching user with {contact_type}={contact}")
        
        if contact_type == 'email':
            user = User.objects.filter(email__iexact=contact).first()
            if not user:
                logger.warning(f"User with email '{contact}' not found")
                raise serializers.ValidationError({
                    "contact": "Аккаунт с таким email не найден. Попробуйте войти по телефону."
                })
        else:
            normalized = normalize_phone(contact)
            if not normalized:
                logger.warning(f"Invalid phone format: {contact}")
                raise serializers.ValidationError({
                    "contact": "Неверный формат телефона"
                })
            user = User.objects.filter(phone=normalized).first()
            if not user:
                logger.warning(f"User with phone '{normalized}' not found")
                raise serializers.ValidationError({
                    "contact": "Аккаунт с таким телефоном не найден. Попробуйте войти по email."
                })
        
        logger.debug(f"User found: {user.email if user else 'None'}")
        return user

    def _validate_password(self, user, password):
        if not user.check_password(password):
            logger.warning(f"Invalid password for user: {user.email}")
            raise serializers.ValidationError({
                "password": "Неверный пароль"
            })
        logger.debug(f"Password valid for user: {user.email}")

    def _validate_active(self, user):
        if not user.is_active:
            logger.warning(f"User account is inactive: {user.email}")
            raise serializers.ValidationError({
                "contact": "Аккаунт деактивирован. Обратитесь к менеджеру."
            })
        logger.debug(f"User is active: {user.email}")

    def create(self, validated_data):
        user = validated_data['user']
        response = generate_jwt_response(user)
        if not user.is_email_verified:
            response['hint'] = 'Рекомендуем подтвердить email для получения ваучеров'

        return response 


class PasswordResetSerializer(serializers.Serializer):
    contact = serializers.CharField(required=True)
    contact_type = serializers.ChoiceField(
        choices=['email', 'phone'],
        required=False
    )

    def validate(self, attrs):
        contact = attrs['contact'].strip()
        contact_type = attrs.get('contact_type')

        if not contact_type:
            contact_type = 'email' if '@' in contact else 'phone'

        user = self._find_user(contact, contact_type)
        attrs['user'] = user
        return attrs

    def _find_user(self, contact, contact_type):
        if contact_type == 'email':
            user = User.objects.filter(email__iexact=contact).first()
            if not user:
                raise serializers.ValidationError("Аккаунт с таким email не найден")
        else:
            normalized = normalize_phone(contact)
            if not normalized:
                raise serializers.ValidationError("Неверный формат телефона")
            user = User.objects.filter(phone=normalized).first()
            if not user:
                raise serializers.ValidationError("Аккаунт с таким телефоном не найден")
        return user

    def save(self):
        from .tasks import send_password_reset_email_task

        user = self.validated_data['user']
        request = self.context.get('request')
        domain, protocol = get_domain_and_protocol(request)
        
        send_password_reset_email_task.delay(user.id, domain, protocol)
        
        response = {
            'message': 'Ссылка для сброса пароля отправлена на ваш email',
        }
        
        if user.email:
            response['email_hint'] = mask_email(user.email)
        
        response['fallback'] = (
            'Не получили письмо? Позвоните менеджеру: +7-XXX-XXX-XX-XX'
        )
        
        logger.info(f"Password reset email queued for {user.email}")
        return response


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    new_password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Пароль должен быть не менее 8 символов")
        if value.isdigit():
            raise serializers.ValidationError("Пароль не может состоять только из цифр")
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({
                'new_password2': 'Пароли не совпадают'
            })
        return attrs

    def save(self):
        user = self.context['user']
        user.set_password(self.validated_data['new_password'])
        user.save(update_fields=['password'])
        return {
            'message': 'Пароль успешно изменён. Теперь вы можете войти.',
            'login_url': '/api/accounts/login/'
        }


class VerifyEmailSerializer(serializers.Serializer):
    """Сериализатор для отправки письма подтверждения (данные не нужны)"""
    pass


class VerifyEmailConfirmSerializer(serializers.Serializer):
    """Сериализатор для подтверждения email"""
    def save(self):
        user = self.context['user']
        user.is_email_verified = True
        user.save(update_fields=['is_email_verified'])
        return {'message': 'Email успешно подтверждён'}


class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'phone',
            'first_name', 'last_name', 'patronymic', 'full_name',
            'date_joined', 'is_email_verified'
        ]
        read_only_fields = ['id', 'email', 'date_joined', 'is_email_verified', 'full_name']

    def get_full_name(self, obj: "CustomUser") -> str:
        return f"{obj.first_name} {obj.last_name} {obj.patronymic}".strip()

    def validate_phone(self, value):
        if not value:
            return value
        normalized = normalize_phone(value)
        if not normalized:
            raise serializers.ValidationError("Неверный формат телефона")
        if User.objects.filter(phone=normalized).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError("Этот телефон уже используется")
        return normalized


class MyTokenObtainPairSerializer(serializers.Serializer):
    """Кастомный сериализатор для JWT (используется с SimpleJWT)"""
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['phone'] = user.phone
        token['is_email_verified'] = user.is_email_verified
        return token
