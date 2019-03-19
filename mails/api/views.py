from rest_framework.generics import ListAPIView, RetrieveAPIView

from mails.api.serializers import MailListSerializer, MailDetailSerializer
from mails.models import Mail


class MailListAPIView(ListAPIView):
    queryset = Mail.objects.all()[:30]
    serializer_class = MailListSerializer


class MailDetailAPIView(RetrieveAPIView):
    queryset = Mail.objects.all()
    serializer_class = MailDetailSerializer


# Example

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class HelloView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        print(request.user.credential_set.all())
        content = {'message': 'Hello, World!'}
        return Response(content)
