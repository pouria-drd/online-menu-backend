from django.db.models import Prefetch
from accounts.constants import UserStatus


def get_optimized_user_queryset():
    """Reusable optimized queryset for users"""
    # Import here to avoid circular import
    from accounts.models import UserModel, UserEmailModel, UserPhoneModel

    qs = (
        UserModel.objects.filter(status=UserStatus.ACTIVE)
        .select_related("profile", "settings")
        .prefetch_related(
            Prefetch(
                "emails",
                queryset=UserEmailModel.objects.filter(is_primary=True).only(
                    "id", "email", "is_verified", "is_primary", "user_id"
                ),
                to_attr="primary_emails",
            ),
            Prefetch(
                "phones",
                queryset=UserPhoneModel.objects.filter(is_primary=True).only(
                    "id", "phone_number", "is_verified", "is_primary", "user_id"
                ),
                to_attr="primary_phones",
            ),
        )
    )

    return qs
