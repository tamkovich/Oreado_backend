from datetime import timedelta

from rest_framework.response import Response
from django.utils import timezone

from shortcuts.shortcuts import post_param_filter_decorator
from mails.api.serializers import MailDetailSerializer
from mails.api.permissions import BasePermission
from mails.api.views_shortcuts import (
    mail_senders_decorator,
    get_mail_or_404
)
from mails.models import Mail, MailSender


class MailAPIView(BasePermission):
    @mail_senders_decorator
    def get(self, request, **kwargs):
        mails = Mail.get_mails_by_user_senders(
            request.user, kwargs['mail_senders'],
            cleaned_date__gte=timezone.now() - timedelta(7),
            viewed=False,
        )
        mails = Mail.process_mail(mails)
        return Response({'data': mails})

    @post_param_filter_decorator('mail_id')
    def post(self, request):
        mail = get_mail_or_404(request.data['mail_id'])
        mail.mark_as_true('viewed')
        return Response({'ok': True})


class FavoriteMailAPIView(BasePermission):
    @mail_senders_decorator
    def get(self, request, **kwargs):
        mails = Mail.get_mails_by_user_senders(
            request.user, kwargs['mail_senders'],
            favourite=True,
        )
        mails = Mail.process_mail(mails)
        return Response({'data': mails})

    @post_param_filter_decorator('mail_id')
    def post(self, request):
        mail = get_mail_or_404(request.data['mail_id'])
        mail.mark_as_true('favourite')
        return Response({'ok': True})


class ArchiveMailAPIView(BasePermission):
    @mail_senders_decorator
    def get(self, request, **kwargs):
        mails = Mail.get_mails_by_user_senders(
            request.user, kwargs['mail_senders'],
            cleaned_date__lte=timezone.now() - timedelta(7),
        )
        mails = Mail.process_mail(mails)
        return Response({'data': mails})


class MailDetailAPIView(BasePermission):
    def get(self, request, pk):
        mail = Mail.objects.get(id=pk)
        return Response({'data': MailDetailSerializer(mail).data})


class SendersListAPIView(BasePermission):
    def get(self, request):
        senders = MailSender.get_active_senders_for_user(request.user)
        return Response({'data': senders})

    @post_param_filter_decorator('selected_senders')
    def post(self, request):
        for inner_id in request.data['selected_senders']:
            try:
                sender = MailSender.objects.get(id=inner_id)
            except MailSender.DoesNotExist:
                return Response({'error': f'Invalid id {inner_id}'})

            sender.selected = True
            sender.save()
        return Response({'ok': True})
