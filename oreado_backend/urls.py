from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'api/mails/',
        include(('mails.api.urls', 'mails.api'), namespace='api-mails')
    ),
    path(
        'api/auth/',
        include(('auth_page.api.urls', 'auth_page'), namespace='auth_page')
    ),
]
