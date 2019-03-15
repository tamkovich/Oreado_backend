from django.contrib.postgres.fields import JSONField
from django.db import models


class Credential(models.Model):
    uuid_token = models.CharField(max_length=100)
    email = models.EmailField(null=True)
    data = JSONField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.email or '<some_credentials>'
