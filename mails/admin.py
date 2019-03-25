from django.contrib import admin

from mails.models import Mail, MailCategory, MailSender


admin.site.register(Mail)
admin.site.register(MailSender)
admin.site.register(MailCategory)
