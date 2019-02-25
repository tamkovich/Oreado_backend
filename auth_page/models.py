from django.db import models
from django.contrib.postgres.fields import JSONField


class UserViewedMail(models.Model):
    client_id = models.TextField()
    message_id = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.client_id} - {self.message_id}"


class MailContent(models.Model):
    message_id = models.CharField(max_length=50)
    content = models.TextField()

    def __str__(self):
        return f"{self.message_id}"


class CredsContent(models.Model):
    email = models.EmailField(null=True)
    data = JSONField()
