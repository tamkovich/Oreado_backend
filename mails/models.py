from django.contrib.auth import get_user_model
from django.db import models

from auth_page.models import Credential


User = get_user_model()


class Mail(models.Model):
    message_id = models.CharField(max_length=250)
    date = models.CharField(max_length=250)
    cleaned_date = models.DateTimeField(blank=True, null=True, default=None)
    come_from = models.CharField(max_length=250)
    come_from_email = models.CharField(max_length=250, blank=True, null=True)
    go_to = models.CharField(max_length=250)
    go_to_email = models.CharField(max_length=250, blank=True, null=True)
    text_body = models.TextField()
    html_body = models.TextField()
    tag_body = models.TextField()
    snippet = models.TextField()
    subject = models.CharField(max_length=250, blank=True, null=True)  # message title
    category = models.ForeignKey(
        "MailCategory", null=True, blank=True, on_delete=models.SET_NULL
    )
    owner = models.ForeignKey(
        Credential, null=True, blank=True, on_delete=models.SET_NULL
    )
    blocked = models.BooleanField(default=False)
    viewed = models.BooleanField(default=False)
    favourite = models.BooleanField(default=False)

    @classmethod
    def get_mails_by_user_senders(cls, user, mail_senders, **kwargs):
        # ToDo: add docstring
        # ToDo: remove not used params **kwargs
        return cls.objects.filter(
            owner__user=user,
            # category_id__in=[3, 2],
            come_from__in=mail_senders
        ).values('id', 'cleaned_date', 'come_from', 'snippet', 'html_body', 'text_body', 'subject')

    @staticmethod
    def process_mail(mails):  # ToDo: remove and use serializer for that goal in every place
        return [
            {
                'id': mail['id'],
                'cleaned_date': mail['cleaned_date'],
                'come_from': mail['come_from'],
                'snippet': mail['snippet'],
                'html_body': mail['html_body'],
                'text_body': mail['text_body'],
                'subject': mail['subject']
            } for mail in mails
        ]

    def mark_as_true(self, attr):
        # ToDo: add docstring
        setattr(self, attr, True)
        self.save()
        return True

    def __str__(self):
        return f"{self.go_to} {self.come_from} {self.text_body[:30]}"


class MailCategory(models.Model):
    name = models.CharField(max_length=250)
    slug = models.SlugField(blank=True)
    css_class = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class MailSender(models.Model):
    name = models.CharField(max_length=250)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    average = models.FloatField(default=1)
    mail_count = models.IntegerField(default=1)

    is_active = models.BooleanField()

    selected = models.BooleanField(default=False)

    class Meta:
        db_table = 'mail_sender'

        verbose_name = 'Mail sender'
        verbose_name_plural = 'Mail senders'

    @classmethod
    def get_senders_name_for_user(cls, user):
        # ToDo: add docstring
        return MailSender.objects.filter(
            user=user, is_active=True, selected=True
        ).values_list('name', flat=True)

    @classmethod
    def get_active_senders_for_user(cls, user):
        # ToDo: add docstring
        return cls.objects.filter(
            user=user, is_active=True
        ).values('id', 'name')

    def __str__(self):
        return self.name
