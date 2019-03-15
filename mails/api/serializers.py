from rest_framework import serializers
from rest_framework.reverse import reverse as api_reverse

from mails.models import Mail


class MailListSerializer(serializers.ModelSerializer):
    uri = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Mail
        fields = [
            'date',
            'come_from',
            'text_body',
            'snippet',
            'viewed',
            'favourite',
            'uri'
        ]

    def get_uri(self, obj):
        request = self.context.get('request')
        return api_reverse("api-mails:detail", kwargs={"pk": obj.id}, request=request)


class MailDetailSerializer(serializers.ModelSerializer):
    uri = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Mail
        fields = [
            'date',
            'come_from',
            'text_body',
            'snippet',
            'viewed',
            'favourite',
            'uri'
        ]

    def get_uri(self, obj):
        request = self.context.get('request')
        return api_reverse("api-mails:detail", kwargs={"pk": obj.id}, request=request)
