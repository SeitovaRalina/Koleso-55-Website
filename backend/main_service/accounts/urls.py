from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView
from .views import (
    RegisterView, CustomTokenObtainPairView, ProfileView,
    GoogleLogin, VKLogin
)

app_name = 'accounts'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('logout/', TokenBlacklistView.as_view(), name='token-blacklist'),
    path('profile/', ProfileView.as_view(), name='profile'),

    path('social/google/', GoogleLogin.as_view(), name='google_login'),
    path('social/vk/', VKLogin.as_view(), name='vk_login'),
]
