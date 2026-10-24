from django.urls import path
from .views import (
    RegisterView, LoginView, ProfileView,
    PasswordResetView, PasswordResetConfirmView,
    VerifyEmailView, VerifyEmailConfirmView,
    CustomTokenRefreshView, CustomTokenBlacklistView,
    GoogleLogin, VKLogin, SocialConfigView
)

app_name = 'accounts'

urlpatterns = [
    # Аутентификация
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('refresh/', CustomTokenRefreshView.as_view(), name='token-refresh'),
    path('logout/', CustomTokenBlacklistView.as_view(), name='token-blacklist'),
    
    # Восстановление пароля
    path('password-reset/', PasswordResetView.as_view(), name='password-reset'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    
    # Подтверждение email
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('verify-email/<uidb64>/<token>/', 
         VerifyEmailConfirmView.as_view(), name='verify-email-confirm'),
    
    # Профиль
    path('profile/', ProfileView.as_view(), name='profile'),

    # Социальная аутентификация
    path('google/', GoogleLogin.as_view(), name='google_login'),
    path('vk/', VKLogin.as_view(), name='vk_login'),
    path('social-config/<str:provider>/', SocialConfigView.as_view(), name='social-config'),
]
