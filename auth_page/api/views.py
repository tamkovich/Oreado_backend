import google.oauth2.credentials

from datetime import datetime

from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from django.conf import settings

from rest_framework.response import Response
from rest_framework.views import APIView

from oreado_backend.celery import load_mails_for_user
from auth_page.api.exception import ParameterError
from mails.models import Credential
from box.gmail.models import Gmail

User = get_user_model()


class AuthAPI(APIView):
    @staticmethod
    def param_validation(data, *args):
        for arg in args:
            if arg not in data:
                raise ParameterError({"error": f"You must pass {arg}"})

    def post(self, request):
        post_data = request.data
        try:
            self.param_validation(
                post_data,
                "accessToken",
                "clientID",
                "refreshToken",
                "scopes",
                "email"
            )
        except ParameterError as err:
            return Response(str(err))

        credentials_data = {
            "token": post_data["accessToken"],
            "scopes": post_data["scopes"],
            "client_id": post_data["clientID"],
            "refresh_token": post_data["refreshToken"],
            "token_uri": settings.AUTH_CONFIG['token_uri'],
            "client_secret": settings.AUTH_CONFIG['client_secret'],
        }
        credentials = google.oauth2.credentials.Credentials(**credentials_data)

        mail = Gmail(creds=credentials)

        if not mail.validate_credentials():
            return Response({'error': 'Invalid credentials'})

        user, created = User.objects.get_or_create(
            email=post_data["email"], username=post_data["email"]
        )

        password = make_password(
            50, post_data["email"] + datetime.now().strftime("%Y%m%d%H%S")
        )

        user.set_password(password)
        user.save()

        cred, created = Credential.objects.get_or_create(
            user=user,
            email=post_data["email"],
            defaults={'credentials': credentials_data}
        )
        load_mails_for_user.delay(credentials_data, cred.id, user.id)

        return Response({"username": post_data["email"], "password": password})
