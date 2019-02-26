from django.db import models
from django.contrib.postgres.fields import JSONField


class CredsContent(models.Model):
    email = models.EmailField(null=True)
    data = JSONField()
