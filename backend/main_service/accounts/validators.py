import re


def normalize_phone(phone):
    """
    Нормализует номер телефона к формату +7XXXXXXXXXX

    Принимает форматы:
    - 8XXXXXXXXXX
    - +7XXXXXXXXXX
    - 9XXXXXXXXX

    Возвращает:
    - +7XXXXXXXXXX (валидный формат)
    - None (невалидный формат)
    """
    if not phone:
        return None

    # Удаляем все нецифровые символы
    phone = re.sub(r'[^\d]', '', phone)

    # Обрабатываем различные форматы
    if phone.startswith('8'):
        phone = '7' + phone[1:]
    elif phone.startswith('9'):
        phone = '7' + phone
    elif not phone.startswith('7'):
        return None

    # Проверяем длину
    if len(phone) != 11:
        return None

    return '+' + phone
