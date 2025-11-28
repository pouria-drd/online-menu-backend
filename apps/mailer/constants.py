from django.db import models


class TemplateType(models.TextChoices):
    CUSTOM = "custom", "Custom Template"
    PREDEFINED = "predefined", "Predefined Template"


class EmailStatus(models.TextChoices):
    SENT = "sent", "Sent"
    FAILED = "failed", "Failed"
    PENDING = "pending", "Pending"
    BOUNCED = "bounced", "Bounced"
