from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema
from .serializers import (
    UserRegisterSerializer,
    UserProfileSerializer,
    MyTokenObtainPairSerializer,
)
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.vk.views import VKOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView


@extend_schema(
    summary="Регистрация пользователя",
    description="Создает нового аккаунта пользователя. Регистрация доступна как по email, так и по номеру телефона. "
                   "После успешной регистрации необходимо войти в систему для получения токена доступа.",
)
class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "message": "Пользователь успешно зарегистрирован",
            "email": user.email
        }, status=status.HTTP_201_CREATED)


@extend_schema(
    summary="Вход в систему",
    description="Аутентификация пользователя по email/телефону и паролю. "
                   "Возвращает JWT токены доступа и обновления для работы с API.",
)
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


@extend_schema(
    summary="Получение и обновление профиля",
    description="Возвращает данные текущего пользователя и позволяет обновить их. "
                   "Требует JWT токен доступа в заголовке Authorization: Bearer <token>.",
)
class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

@extend_schema(
    summary="Вход через Google",
    description="Аутентификация пользователя через аккаунт Google OAuth2. "
                   "Требует передачи access_token от Google. Создает или находит существующего пользователя.",
)
class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client

@extend_schema(
    summary="Обновление JWT токена",
    description="Обновляет JWT токен доступа с помощью refresh токена. "
                   "Refresh токен действителен 7 дней. Требует валидный refresh токен.",
)
class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = TokenRefreshView

@extend_schema(
    summary="Выход из системы",
    description="Разлогинивает пользователя, добавляя текущий refresh токен в черный список. "
                   "Требует JWT токен доступа. После выхода все токены становятся недействительными.",
)
class CustomTokenBlacklistView(TokenBlacklistView):
    serializer_class = TokenBlacklistView

@extend_schema(
    summary="Вход через ВКонтакте",
    description="Аутентификация пользователя через аккаунт ВКонтакте OAuth2. "
                   "Требует передачи access_token от VK. Создает или находит существующего пользователя.",
)
class VKLogin(SocialLoginView):
    adapter_class = VKOAuth2Adapter
    client_class = OAuth2Client
