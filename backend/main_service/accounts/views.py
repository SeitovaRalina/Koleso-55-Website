from rest_framework import generics, status, permissions, serializers
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import OpenApiParameter, extend_schema, OpenApiTypes
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from .serializers import (
    CustomRegisterSerializer,
    LoginSerializer,
    UserProfileSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer,
    VerifyEmailSerializer,
    VerifyEmailConfirmSerializer
)
from .utils import link_guest_bookings
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.vk.views import VKOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView


@extend_schema(
    summary="Регистрация пользователя",
    description="Создает нового аккаунта пользователя с email (обязательно) и телефоном (опционально). "
                   "Возвращает JWT токены для немедленного входа. Отправляет приветственное письмо.",
)
class RegisterView(generics.GenericAPIView):
    serializer_class = CustomRegisterSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Генерируем JWT токены
        refresh = RefreshToken.for_user(user)
        
        # Привязываем гостевые бронирования
        linking_result = link_guest_bookings(user)
        
        response_data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'email': user.email,
                'phone': user.phone,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'patronymic': user.patronymic,
                'is_email_verified': user.is_email_verified,
            },
            'message': 'Пользователь успешно зарегистрирован',
        }
        
        if linking_result['linked'] > 0:
            response_data['linked_bookings'] = f"Привязано {linking_result['linked']} гостевых бронирований"
        
        if not user.is_email_verified:
            response_data['warning'] = 'Email не подтвержден'
        
        return Response(response_data, status=status.HTTP_201_CREATED)


@extend_schema(
    summary="Вход в систему",
    description="Аутентификация пользователя по email/телефону и паролю. "
                   "Автоматически определяет тип контакта. Возвращает JWT токены.",
)
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.save(), status=status.HTTP_200_OK)


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
        return Response(serializer.save(), status=status.HTTP_200_OK)


@extend_schema(
    summary="Подтверждение сброса пароля",
    description="Устанавливает новый пароль по ссылке из письма. "
                   "Требует uidb64 и token из ссылки сброса.",
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

    def post(self, request, uidb64, token):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.save(), status=status.HTTP_200_OK)


@extend_schema(
    summary="Отправка подтверждения email",
    description="Отправляет письмо со ссылкой для подтверждения email. "
                   "Доступно только для пользователей с неподтвержденным email.",
)
class VerifyEmailView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = VerifyEmailSerializer

    def post(self, request, *args, **kwargs):
        if request.user.is_email_verified:
            return Response(
                {"message": "Email уже подтвержден"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # TODO: Отправка письма подтверждения email
        # send_email_verification(request.user)
        
        return Response(
            {"message": "Письмо с подтверждением отправлено на ваш email"}, 
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
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {"error": "Недействительная ссылка"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        if not default_token_generator.check_token(user, token):
            return Response(
                {"error": "Недействительная или просроченная ссылка"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        user.is_email_verified = True
        user.save()
        
        return Response(
            {"message": "Email успешно подтвержден"}, 
            status=status.HTTP_200_OK
        )


@extend_schema(
    summary="Профиль пользователя",
    description="Получение и обновление данных профиля. "
                   "Email можно только просматривать, телефон можно добавить/изменить. "
                   "При изменении телефона автоматически привязываются гостевые бронирования.",
)
class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        # Сохраняем старый телефон для сравнения
        old_phone = request.user.phone
        
        response = super().update(request, *args, **kwargs)
        
        # Если телефон изменился, запускаем привязку гостевых бронирований
        new_phone = request.user.phone
        if old_phone != new_phone and new_phone:
            linking_result = link_guest_bookings(request.user)
            
            if linking_result['linked'] > 0:
                response.data['linked_bookings'] = f"Привязано {linking_result['linked']} гостевых бронирований"
        
        return response


@extend_schema(
    summary="Вход через Google",
    description="Аутентификация пользователя через аккаунт Google OAuth2. "
                   "Автоматически создает аккаунт или привязывает к существующему по email.",
)
class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client


@extend_schema(
    summary="Вход через ВКонтакте",
    description="Аутентификация пользователя через аккаунт ВКонтакте OAuth2. "
                   "Автоматически создает аккаунт или привязывает к существующему по email.",
)
class VKLogin(SocialLoginView):
    adapter_class = VKOAuth2Adapter
    client_class = OAuth2Client


@extend_schema(
    summary="Обновление JWT токена",
    description="Обновляет JWT токен доступа с помощью refresh токена.",
)
class CustomTokenRefreshView(TokenRefreshView):
    pass


@extend_schema(
    summary="Выход из системы",
    description="Разлогинивает пользователя, добавляя refresh токен в черный список.",
)
class CustomTokenBlacklistView(TokenBlacklistView):
    pass
