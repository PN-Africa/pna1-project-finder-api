import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    email = models.EmailField(unique=True, editable=False)
    professional_role = models.CharField(max_length=255, null=True)
    deactivated_at = models.DateTimeField(default=None, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]