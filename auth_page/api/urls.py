from rest_framework_simplejwt import views

from django.urls import path

from auth_page.api.views import (
    AuthAPI
)


app_name = "auth-api"

urlpatterns = [
    path(
        'token/',
        views.TokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),
    path(
        'token/refresh/',
        views.TokenRefreshView.as_view(),
        name='token_refresh'
    ),

    path('credentials/', AuthAPI.as_view(), name='credentials')
]
