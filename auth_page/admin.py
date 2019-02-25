from django.contrib import admin

from .models import UserViewedMail, MailContent


admin.site.register(UserViewedMail)
admin.site.register(MailContent)
