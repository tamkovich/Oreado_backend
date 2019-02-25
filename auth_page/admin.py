from django.contrib import admin

from .models import UserViewedMail, MailContent, CredsContent


admin.site.register(UserViewedMail)
admin.site.register(MailContent)
admin.site.register(CredsContent)
