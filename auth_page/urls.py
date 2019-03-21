from django.urls import path

from auth_page.views import clear_credentials, oauth2callback, authorize, revoke

app_name = "auth_page"

urlpatterns = [
    path("authorize/", authorize, name="authorize"),
    path("oauth2callback/", oauth2callback, name="oauth2callback"),
    path("revoke/", revoke, name="revoke"),
    path("clear/", clear_credentials, name="clear"),
]
