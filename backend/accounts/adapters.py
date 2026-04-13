from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

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
        user = super().save_user(request, sociallogin, form)
        extra_data = sociallogin.account.extra_data
        user.first_name = extra_data.get('given_name', '') or extra_data.get('first_name', '')
        user.last_name = extra_data.get('family_name', '') or extra_data.get('last_name', '')
        user.save(update_fields=['first_name', 'last_name'])
        return user
