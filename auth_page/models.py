from django.db import models
from django.db.models.aggregates import Count
from django.contrib.postgres.fields import JSONField
from random import randint


class GmailMailManager(models.Manager):
    def random(self):
        count = self.aggregate(count=Count('id'))['count']
        random_index = randint(0, count - 1)
        return self.all()[random_index]


class CredsContent(models.Model):
    email = models.EmailField(null=True)
    data = JSONField()


class GmailMails(models.Model):
    message_id = models.CharField(max_length=100)
    date = models.CharField(max_length=50)
    come_from = models.CharField(max_length=50)
    go_to = models.CharField(max_length=50)
    text_body = models.TextField()
    html_body = models.TextField()
    snippet = models.TextField()
    category = models.ForeignKey('MailCategory', null=True, blank=True, on_delete=models.SET_NULL)
    owner = models.ForeignKey('CredsContent', null=True, blank=True, on_delete=models.SET_NULL)

    objects = GmailMailManager()


class MailCategory(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField()
