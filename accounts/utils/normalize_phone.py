import re


def normalize_phone(phone: str) -> str:
    """
    Convert Persian numbers to English, remove spaces,
    and convert local Iranian phone numbers starting with 0
    to international format starting with +98.

    Args:
        phone (str): The phone number to be normalized

    Returns:
        str: The normalized phone number in international format
    """
    persian_to_english = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")
    phone = phone.translate(persian_to_english)
    phone = re.sub(r"\s+", "", phone)

    return phone
