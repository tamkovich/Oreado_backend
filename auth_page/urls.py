from django.urls import path

from .views import (
    clear_credentials,
    oauth2callback,
    authorize,
    revoke,

    DeleteFromViewed,
    DetailPage,
    MainPage,
)


urlpatterns = [
    path('', MainPage.as_view(), name='main'),
    path('<slug:message_id>', DetailPage.as_view(), name='detail'),
    path('delete/<slug:message_id>', DeleteFromViewed.as_view(), name='detail'),
    path('authorize/', authorize, name='authorize'),
    path('oauth2callback/', oauth2callback, name='oauth2callback'),
    path('revoke/', revoke, name='revoke'),
    path('clear/', clear_credentials, name='clear'),
]
