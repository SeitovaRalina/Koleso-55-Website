import re

def normalize_phone(phone):
    """Нормализация телефона в формат +7XXXXXXXXXX"""
    if not phone:
        return None
    digits = re.sub(r'[^\d]', '', phone)
    if len(digits) == 11 and digits.startswith('8'):
        return '+7' + digits[1:]
    elif len(digits) == 11 and digits.startswith('7'):
        return '+' + digits
    elif len(digits) == 10 and digits.startswith('9'):
        return '+7' + digits
    return None

def mask_email(email):
    """Маскирует email: iv***@mail.ru"""
    if '@' not in email:
        return email
    name, domain = email.split('@')
    return name[:2] + '***@' + domain


def mask_phone(phone):
    """Маскирует телефон: +7900***67"""
    if not phone or len(phone) < 6:
        return phone
    return phone[:5] + '***' + phone[-2:]

