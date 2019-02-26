from django.db import models
from django.contrib.postgres.fields import JSONField


class CredsContent(models.Model):
    email = models.EmailField(null=True)
    data = JSONField()


class GmailMails(models.Model):
    message_id = models.CharField(max_length=100)
    date = models.CharField(max_length=50)
    come_from = models.CharField(max_length=50)
    go_to = models.CharField(max_length=50)
    body = models.TextField()
    snippet = models.TextField()
    category = models.ForeignKey('MailCategory', null=True, blank=True, on_delete=models.SET_NULL)
    owner = models.ForeignKey('CredsContent', null=True, blank=True, on_delete=models.SET_NULL)


class MailCategory(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField()
