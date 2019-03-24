from datetime import timedelta

from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authentication import (
    SessionAuthentication,
    BasicAuthentication
)
from rest_framework.views import APIView
from django.utils import timezone

from mails.api.serializers import MailListSerializer, MailDetailSerializer
from mails.models import Mail

from mails.models import MailSender


class MailListAPIView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        mails = Mail.objects.filter(
            owner__user=request.user,
            cleaned_date__gte=timezone.now() + timedelta(7),
            viewed=False,
            category_id__in=[3, 2]
        ).values('id', 'cleaned_date', 'come_from', 'snippet', 'text_body')

        return Response({'data': mails})


class MailDetailAPIView(RetrieveAPIView):
    queryset = Mail.objects.all()
    serializer_class = MailDetailSerializer


class SendersListAPIView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        senders = MailSender.objects.filter(
            user=request.user, is_active=True
        )
        return Response({'data': senders.values('id', 'name')})
