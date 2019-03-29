from django.urls import path, re_path

from mails.api.views import (
    MailDetailAPIView,
    MailAPIView,
    SendersListAPIView,
    FavoriteMailAPIView,
    ArchiveMailAPIView
)


app_name = "mails-api"

urlpatterns = [
    path("", MailAPIView.as_view(), name="list"),
    path("favorite/", FavoriteMailAPIView.as_view(), name="favorite"),
    path("archive/", ArchiveMailAPIView.as_view(), name="archive"),
    path("senders/", SendersListAPIView.as_view(), name="sender_list"),
    re_path(r"^(?P<pk>\d+)/$", MailDetailAPIView.as_view(), name="detail"),
]
