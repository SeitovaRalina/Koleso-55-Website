import logging
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from .serializers import (
    CustomRegisterSerializer,
    LoginSerializer,
    UserProfileSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer,
    VerifyEmailSerializer,
    VerifyEmailConfirmSerializer,
)
from .utils import link_guest_bookings, generate_jwt_response, get_domain_and_protocol
from .tasks import send_verification_email_task

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.vk.views import VKOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView

logger = logging.getLogger(__name__)
User = get_user_model()


class SocialConfigView(generics.GenericAPIView):
    """Expose public OAuth client IDs; never expose provider secrets."""
    permission_classes = [permissions.AllowAny]

    def get(self, request, provider):
        clients = {
            'google': getattr(settings, 'GOOGLE_CLIENT_ID', ''),
            'vk': getattr(settings, 'VK_CLIENT_ID', ''),
        }
        if provider not in clients:
            return Response({'detail': 'Unknown provider.'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'client_id': clients[provider]})


# ============================================================
# REGISTRATION
# ============================================================

@extend_schema(
    summary="Регистрация пользователя",
    description="Создаёт аккаунт с email (обязательно) и телефоном (опционально). "
                "Возвращает JWT токены, привязывает гостевые бронирования и отправляет приветственное письмо подтверждения.",
)
class RegisterView(generics.GenericAPIView):
    serializer_class = CustomRegisterSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        response = generate_jwt_response(user)

        # Привязываем гостевые бронирования
        linking_result = link_guest_bookings(user)
        if linking_result.get('linked'):
            response['linked_bookings'] = linking_result['linked']

        if not user.is_email_verified:
            response['hint'] = 'Email не подтверждён. Проверьте почту.'

        logger.info(f"User registered: {user.email}")
        return Response(response, status=status.HTTP_201_CREATED)


# ============================================================
# LOGIN
# ============================================================

@extend_schema(
    summary="Вход в систему",
    description="Аутентификация пользователя по email/телефону и паролю. "
                   "Автоматически определяет тип контакта. Возвращает JWT токены.",
)
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        logger.debug(f"Login attempt with data: {request.data}")
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"Login validation failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        result = serializer.save()
        logger.info(f"User logged in successfully")
        return Response(result, status=status.HTTP_200_OK)


# ============================================================
# PASSWORD RESET
# ============================================================

@extend_schema(
    summary="Сброс пароля",
    description="Отправляет ссылку для сброса пароля на email пользователя. "
                   "Можно использовать email или телефон для поиска аккаунта.",
)
class PasswordResetView(generics.GenericAPIView):
    serializer_class = PasswordResetSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response(result, status=status.HTTP_200_OK)


@extend_schema(
    summary="Подтверждение сброса пароля",
    description="Устанавливает новый пароль по ссылке из письма. "
                "Требует uidb64 и token из ссылки для сброса."
                "GET запрос проверяет валидность ссылки, POST устанавливает новый пароль.",
    parameters=[
        OpenApiParameter(
            name='uidb64',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description='Base64-кодированный ID пользователя',
            required=True,
        ),
        OpenApiParameter(
            name='token',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description='Токен сброса пароля',
            required=True,
        ),
    ],
)
class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request, uidb64, token):
        user = self._get_user(uidb64, token)
        if not user:
            return Response(
                {'error': 'Ссылка недействительна или устарела'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response({
            'message': 'Ссылка действительна. Введите новый пароль.',
            'valid': True
        })

    def post(self, request, uidb64, token):
        user = self._get_user(uidb64, token)
        if not user:
            return Response(
                {'error': 'Ссылка недействительна или устарела. Запросите новую.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data, context={'user': user})
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response(result, status=status.HTTP_200_OK)

    def _get_user(self, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return None
        if not default_token_generator.check_token(user, token):
            return None
        return user


# ============================================================
# EMAIL VERIFICATION
# ============================================================

@extend_schema(
    summary="Отправка письма подтверждения email",
    description="Отправляет письмо со ссылкой для подтверждения email. "
                   "Доступно только для пользователей с неподтвержденным email. "
                   "Rate limit: 1 запрос в 60 секунд.",
)
class VerifyEmailView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = VerifyEmailSerializer

    def post(self, request, *args, **kwargs):
        user = request.user
        
        if user.is_email_verified:
            return Response(
                {"message": "Email уже подтверждён"},
                status=status.HTTP_200_OK
            )

        # Rate limiting
        cache_key = f"email_verification:{user.id}"
        if cache.get(cache_key):
            ttl = cache.ttl(cache_key)
            return Response(
                {
                    "error": "Слишком много запросов",
                    "retry_after_seconds": ttl
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        cache.set(cache_key, True, 60)
        
        domain, protocol = get_domain_and_protocol(request)
        send_verification_email_task.delay(user.id, domain, protocol)

        return Response(
            {"message": "Письмо с подтверждением отправлено"},
            status=status.HTTP_200_OK
        )


@extend_schema(
    summary="Подтверждение email по ссылке",
    description="Подтверждает email пользователя по ссылке из письма. "
                   "Требует uidb64 и token из ссылки подтверждения.",
    parameters=[
        OpenApiParameter(
            name='uidb64',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description='Base64-кодированный ID пользователя',
            required=True,
        ),
        OpenApiParameter(
            name='token',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description='Токен подтверждения',
            required=True,
        )
    ],
)
class VerifyEmailConfirmView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = VerifyEmailConfirmSerializer

    def get(self, request, uidb64, token):
        user = self._get_user(uidb64, token)
        if not user:
            return Response(
                {"error": "Недействительная или просроченная ссылка"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user.is_email_verified:
            return Response(
                {"message": "Email уже подтверждён"},
                status=status.HTTP_200_OK
            )

        serializer = self.get_serializer(context={'user': user})
        result = serializer.save()
        return Response(result, status=status.HTTP_200_OK)

    def _get_user(self, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return None
        if not default_token_generator.check_token(user, token):
            return None
        return user


# ============================================================
# PROFILE
# ============================================================

@extend_schema(
    summary="Профиль пользователя",
    description="Просмотр и редактирование профиля. При смене телефона привязываются гостевые бронирования.",
)
class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        old_phone = self.request.user.phone
        user = serializer.save()

        if old_phone != user.phone and user.phone:
            linking_result = link_guest_bookings(user)
            if linking_result.get('linked'):
                # Сохраняем в сериализатор для ответа
                serializer._linked_bookings = linking_result['linked']

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        linked = getattr(self.get_serializer(), '_linked_bookings', 0)
        if linked:
            response.data['linked_bookings'] = f"Привязано {linked} гостевых бронирований"
        return response


# ============================================================
# SOCIAL AUTH
# ============================================================

@extend_schema(summary="Вход через Google")
class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client


@extend_schema(summary="Вход через ВКонтакте")
class VKLogin(SocialLoginView):
    adapter_class = VKOAuth2Adapter
    client_class = OAuth2Client


# ============================================================
# JWT TOKENS
# ============================================================

@extend_schema(summary="Обновление JWT токена")
class CustomTokenRefreshView(TokenRefreshView):
    pass


@extend_schema(summary="Выход из системы (blacklist refresh токена)")
class CustomTokenBlacklistView(TokenBlacklistView):
    pass
