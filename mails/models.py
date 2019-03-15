from django.db import models
from django.db.models.aggregates import Count
from random import randint

from auth_page.models import Credential


class MailManager(models.Manager):
    def random(self):
        qs = self.filter(category__isnull=True).filter(blocked=False)
        count = qs.aggregate(count=Count('id'))['count']
        random_index = randint(0, count - 1)
        return qs.filter(category__isnull=True).filter(blocked=False)[random_index]


class Mail(models.Model):
    message_id = models.CharField(max_length=100)
    date = models.CharField(max_length=100)
    come_from = models.CharField(max_length=100)
    go_to = models.CharField(max_length=100)
    text_body = models.TextField()
    html_body = models.TextField()
    tag_body = models.TextField()
    snippet = models.TextField()
    category = models.ForeignKey('MailCategory', null=True, blank=True, on_delete=models.SET_NULL)
    owner = models.ForeignKey(Credential, null=True, blank=True, on_delete=models.SET_NULL)
    blocked = models.BooleanField(default=False)
    viewed = models.BooleanField(default=False)
    favourite = models.BooleanField(default=False)

    objects = MailManager()


class MailCategory(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(blank=True)
    css_class = models.CharField(max_length=30)

    def __str__(self):
        return self.name
