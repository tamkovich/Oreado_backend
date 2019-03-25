from datetime import timedelta

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone

from mails.api.serializers import MailDetailSerializer
from mails.models import Mail

from mails.models import MailSender


class MailListAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        mail_senders = MailSender.objects.filter(
            user=request.user, is_active=True, selected=True
        ).values_list('name', flat=True)

        mails = Mail.objects.filter(
            owner__user=request.user,
            cleaned_date__gte=timezone.now() - timedelta(7),
            viewed=False,
            category_id__in=[3, 2],
            come_from__in=mail_senders
        ).values('id', 'cleaned_date', 'come_from', 'snippet', 'text_body')

        data_to_send = []

        for mail in mails:
            data_to_send.append({
                'id': mail['id'],
                'cleaned_date': mail['cleaned_date'],
                'come_from': mail['come_from'],
                'snippet': mail['snippet'],
                'text_body': mail['text_body'][:150],
            })
        return Response({'data': mails})


class MailDetailAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        mail = Mail.objects.get(id=pk)
        return Response({'data': MailDetailSerializer(mail).data})


class SendersListAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        senders = MailSender.objects.filter(
            user=request.user, is_active=True
        )
        return Response({'data': senders.values('id', 'name')})

    def post(self, request):
        ids = request.data.get('selected_senders')
        if not ids:
            return Response({'error': 'You must pass "selected_senders"'})
        for inner_id in ids:
            try:
                sender = MailSender.objects.get(id=inner_id)
            except MailSender.DoesNotExist:
                return Response({'error': f'Invalid id {inner_id}'})

            sender.selected = True
            sender.save()

        return Response({'ok': True})
