from datetime import datetime

from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from django.conf import settings

from rest_framework.response import Response
from rest_framework.views import APIView

from oreado_backend.celery import load_mails_for_user
from auth_page.models import Credential

from shortcuts.shortcuts import (
    post_param_filter_decorator,
    credentials_data_to_gmail
)

User = get_user_model()


class AuthAPI(APIView):
    @staticmethod
    def request_data_to_credentials_data(data):
        return {
            "token": data["accessToken"],
            "scopes": data["scopes"],
            "client_id": data["clientID"],
            "refresh_token": data["refreshToken"],
            "token_uri": settings.AUTH_CONFIG['token_uri'],
            "client_secret": settings.AUTH_CONFIG['client_secret'],
        }

    @post_param_filter_decorator(
        'accessToken', 'clientID', 'refreshToken', 'scopes', 'email'
    )
    def post(self, request):
        credentials_data = self.request_data_to_credentials_data(request.data)
        mail = credentials_data_to_gmail(credentials_data)
        print(request.data)

        if not mail.validate_credentials():
            return Response({'error': 'Invalid credentials'})

        user, created = User.objects.get_or_create(
            email=request.data["email"], username=request.data["email"]
        )
        password = make_password(
            50, request.data["email"] + datetime.now().strftime("%Y%m%d%H%S")
        )
        user.set_password(password)
        user.save()

        cred, created = Credential.objects.get_or_create(
            user=user,
            email=request.data["email"],
            defaults={'credentials': credentials_data}
        )
        load_mails_for_user.delay(credentials_data, cred.id, user.id)

        return Response(
            {"username": request.data["email"], "password": password}
        )
