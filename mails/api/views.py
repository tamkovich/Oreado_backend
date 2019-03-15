from rest_framework.generics import ListAPIView, RetrieveAPIView

from mails.api.serializers import MailListSerializer, MailDetailSerializer
from mails.models import Mail


class MailListAPIView(ListAPIView):
    queryset = Mail.objects.all()[:30]
    serializer_class = MailListSerializer


class MailDetailAPIView(RetrieveAPIView):
    queryset = Mail.objects.all()
    serializer_class = MailDetailSerializer
