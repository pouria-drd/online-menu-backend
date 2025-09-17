from random import choices


def generate_otp_code(length: int = 5) -> str:
    """Generate a random OTP code."""
    code: str = "".join(choices("0123456789", k=length))
    return code
