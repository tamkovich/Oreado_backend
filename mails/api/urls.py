from django.urls import path, re_path

from mails.api.views import (
    MailDetailAPIView,
    MailListAPIView,
    SendersListAPIView
)


app_name = "mails-api"

urlpatterns = [
    path("", MailListAPIView.as_view(), name="list"),
    path("senders/", SendersListAPIView.as_view(), name="sender_list"),
    re_path(r"^(?P<pk>\d+)/$", MailDetailAPIView.as_view(), name="detail"),
]
