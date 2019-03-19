from django.urls import path, re_path

from mails.api.views import (
    MailDetailAPIView,
    MailListAPIView,
    HelloView
)

app_name = "mails-api"

urlpatterns = [
    path('', MailListAPIView.as_view(), name='list'),
    re_path(r'^(?P<pk>\d+)/$', MailDetailAPIView.as_view(), name='detail'),

    # Example
    path('hello/', HelloView.as_view(), name='hello'),

]
