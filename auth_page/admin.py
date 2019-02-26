from django.contrib import admin

from .models import CredsContent, GmailMails, MailCategory

admin.site.register(CredsContent)
admin.site.register(GmailMails)
admin.site.register(MailCategory)
