from django.urls import path

from .views import (
    clear_credentials,
    oauth2callback,
    authorize,
    revoke,
    home,
)

urlpatterns = [
    path('', home, name='home'),
    path('authorize/', authorize, name='authorize'),
    path('oauth2callback/', oauth2callback, name='oauth2callback'),
    path('revoke/', revoke, name='revoke'),
    path('clear/', clear_credentials, name='clear'),
]
