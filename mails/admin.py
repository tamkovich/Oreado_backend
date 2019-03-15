from django.contrib import admin

from mails.models import Mail, MailCategory

admin.site.register(Mail)
admin.site.register(MailCategory)
