import google.oauth2.credentials

from datetime import datetime

from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from django.conf import settings

from rest_framework.response import Response
from rest_framework.views import APIView


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
            "token": request.POST["accessToken"],
            "scopes": request.POST["scopes"],
            "client_id": request.POST["clientID"],
            "refresh_token": request.POST["refreshToken"],
            "token_uri": settings.AUTH_CONFIG['token_uri'],
            "client_secret": settings.AUTH_CONFIG['client_secret'],
        }
        credentials = google.oauth2.credentials.Credentials(**credentials_data)

        mail = Gmail(creds=credentials)

        print(mail.validate_credentials())

        user, created = User.objects.get_or_create(
            email=post_data["email"], username=post_data["email"]
        )

        password = make_password(
            50, post_data["email"] + datetime.now().strftime("%Y%m%d%H%S")
        )

        user.set_password(password)

        Credential.objects.get_or_create(
            user=user,
            email=request.POST["email"],
            defaults={'credentials': credentials_data}
        )

        return Response({"username": post_data["email"], "password": password})
