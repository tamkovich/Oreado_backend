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
        mails = Mail.objects.filter(
            owner__user=request.user,
            cleaned_date__gte=timezone.now() - timedelta(7),
            viewed=False,
            category_id__in=[3, 2]
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
