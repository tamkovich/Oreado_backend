from django.urls import path, re_path

from .views import (
    clear_credentials,
    oauth2callback,
    authorize,
    revoke,
    home,
    classify,
)

app_name = 'auth_page'

urlpatterns = [
    path('', home, name='home'),
    re_path('^classify/(?P<cat_slug>[-\w]+)/(?P<mail_id>\d+)/$', classify, name='classify'),
    path('authorize/', authorize, name='authorize'),
    path('oauth2callback/', oauth2callback, name='oauth2callback'),
    path('revoke/', revoke, name='revoke'),
    path('clear/', clear_credentials, name='clear'),
]
