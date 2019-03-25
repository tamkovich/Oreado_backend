from django.contrib.auth import get_user_model
from django.db import models

from auth_page.models import Credential


User = get_user_model()


class Mail(models.Model):
    message_id = models.CharField(max_length=100)
    date = models.CharField(max_length=100)
    cleaned_date = models.DateTimeField(blank=True, null=True, default=None)
    come_from = models.CharField(max_length=100)
    come_from_email = models.CharField(max_length=100, blank=True, null=True)
    go_to = models.CharField(max_length=100)
    go_to_email = models.CharField(max_length=100, blank=True, null=True)
    text_body = models.TextField()
    html_body = models.TextField()
    tag_body = models.TextField()
    snippet = models.TextField()
    category = models.ForeignKey(
        "MailCategory", null=True, blank=True, on_delete=models.SET_NULL
    )
    owner = models.ForeignKey(
        Credential, null=True, blank=True, on_delete=models.SET_NULL
    )
    blocked = models.BooleanField(default=False)
    viewed = models.BooleanField(default=False)
    favourite = models.BooleanField(default=False)


class MailCategory(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(blank=True)
    css_class = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class MailSender(models.Model):
    name = models.CharField(max_length=150)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    average = models.FloatField(default=1)
    mail_count = models.IntegerField(default=1)

    is_active = models.BooleanField()

    selected = models.BooleanField(default=False)

    class Meta:
        db_table = 'mail_sender'

        verbose_name = 'Mail sender'
        verbose_name_plural = 'Mail senders'

    def __str__(self):
        return f"{self.name}"
