from django.contrib.postgres.fields import JSONField
from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Credential(models.Model):
    user = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.SET_NULL
    )

    email = models.EmailField(null=True)
    credentials = JSONField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.email or "<some_credentials>"
