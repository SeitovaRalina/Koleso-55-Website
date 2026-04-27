from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from .utils import link_guest_bookings

User = get_user_model()


class CustomAccountAdapter(DefaultAccountAdapter):
    def set_phone(self, user, phone: str, verified: bool):
        user.phone = phone
        user.save(update_fields=['phone'])

    def get_phone(self, user):
        phone = getattr(user, 'phone', None)
        if not phone:
            return None
        return (phone, False)

    def set_phone_verified(self, user, phone: str):
        if getattr(user, 'phone', None) != phone:
            self.set_phone(user, phone, verified=True)

    def get_user_by_phone(self, phone: str):
        if not phone:
            return None
        try:
            return User.objects.get(phone=phone)
        except User.DoesNotExist:
            return None

    def send_verification_code_sms(self, user, phone: str, code: str, **kwargs):
        raise NotImplementedError('Phone verification SMS sending is not configured.')


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        """
        Сохраняет пользователя при социальном входе.
        Автоматически привязывает гостевые бронирования и помечает email как подтвержденный.
        """
        user = super().save_user(request, sociallogin, form)
        extra_data = sociallogin.account.extra_data
        
        # Заполняем имя из социальных данных (разные источники для разных платформ)
        first_name = (extra_data.get('given_name') or 
                     extra_data.get('first_name') or 
                     extra_data.get('name', '').split()[0] if extra_data.get('name') else '')
        
        last_name = (extra_data.get('family_name') or 
                    extra_data.get('last_name') or 
                    ' '.join(extra_data.get('name', '').split()[1:]) if extra_data.get('name') and len(extra_data.get('name', '').split()) > 1 else '')
        
        # Всегда обновляем имя и фамилию из социальных сетей
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
            
        # Email из социальных сетей считаем подтвержденным
        if sociallogin.account.email and not user.is_email_verified:
            user.is_email_verified = True
            
        user.save()
        
        # Привязываем гостевые бронирования
        if request:
            link_guest_bookings(user)
        
        return user
    
    def pre_social_login(self, request, sociallogin):
        """
        Обрабатывает предварительный вход через социальную сеть.
        Если пользователь с таким email уже существует, привязываем социальный аккаунт.
        """
        email = sociallogin.account.email
        if email:
            try:
                existing_user = User.objects.get(email=email)
                # Привязываем социальный аккаунт к существующему пользователю
                sociallogin.connect(request, existing_user)
            except User.DoesNotExist:
                # Пользователь новый, будет создан автоматически
                pass
    
    def new_user(self, request, sociallogin):
        """
        Создает нового пользователя для социального входа.
        """
        email = sociallogin.account.email
        if not email:
            # Если email не предоставлен, используем временный
            email = f"social_{sociallogin.account.uid}@social.local"
        
        user = User(
            email=email,
            is_email_verified=bool(sociallogin.account.email),
        )
        return user
