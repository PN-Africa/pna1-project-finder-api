import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

from core.models import BaseModel


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    email = models.EmailField(unique=True, editable=False)
    professional_role = models.CharField(max_length=255, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]


# class Profile(BaseModel):
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="profile"
#     )
#     professional_role = models.CharField(max_length=255, null=True)

#     def __str__(self):
#         return f"<Profile: user={self.user_id} professional_role={self.professional_role}>"
