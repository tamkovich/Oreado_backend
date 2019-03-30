from django.contrib import admin

from mails.models import Mail, MailCategory, MailSender


class MailAdmin(admin.ModelAdmin):
    search_fields = ('come_from', 'go_to', 'text_body')


admin.site.register(Mail, MailAdmin)

admin.site.register(MailSender)
admin.site.register(MailCategory)
