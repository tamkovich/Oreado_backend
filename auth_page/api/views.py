from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model

from rest_framework.response import Response
from rest_framework.views import APIView

from mails.models import Credential


User = get_user_model()


class AuthAPI(APIView):
    @staticmethod
    def param_validation(data, *args):
        for arg in args:
            if arg not in data:
                return Response({'error': f'You must pass {arg}'})

    def post(self, request):
        self.param_validation(
            request.POST, 'accessToken', 'clientID', 'refreshToken', 'scopes',
            'email'
        )

        data = {
            'token': request.POST['accessToken'],
            'scopes': request.POST['scopes'],
            'client_id': request.POST['clientID'],
            'refresh_token': request.POST['refreshToken'],
            'token_uri': "https://oauth2.googleapis.com/token",
            'client_secret': "Sh39oZYEi1y5aau0v6vYZ-ry"
        }

        user, created = User.objects.get_or_create(email=request.POST['email'])

        password = make_password(50, request.POST['email'])

        user.set_password(password)

        Credential.objects.create(
            user=user, email=request.POST['email'], data=data
        )

        return Response(
            {'username': request.POST['email'], 'password': password}
        )
