import json
import requests

import google.oauth2.credentials
import google_auth_oauthlib.flow
from oauth2client import client

from functools import wraps

from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.conf import settings
from django.urls import reverse

from rest_framework.response import Response
from rest_framework.views import APIView

from auth_page.models import UserViewedMail, MailContent, CredsContent
from box.gmail.models import Gmail


def cred_check_decorator(func):
    @wraps(func)
    def inner(*args, **kwargs):
        request = args[1]
        if request.method == 'POST':
            credentials = request.POST.get('credentials')
        elif request.method == 'GET':
            credentials = request.GET.get('credentials')
        else:
            credentials = None

        if credentials:
            credentials = json.loads(credentials)
            credentials = google.oauth2.credentials.Credentials(**credentials)
        return func(*args, **kwargs, credentials=credentials)
    return inner


class MainPage(APIView):

    @cred_check_decorator
    def get(self, request, **kwargs):
        mail = Gmail(creds=kwargs.get('credentials'))

        messages = []
        messages_ids_threads = mail.list_messages_matching_query(
            'me',
            count_messages=request.GET.get('count_messages', 5)
        )

        messages_id = list(map(lambda mes: mes['id'], messages_ids_threads))

        client_mails = UserViewedMail.objects.values_list('message_id')
        client_mails = list(map(lambda x: x[0], client_mails))
        mail_to_show = set(messages_id) - set(client_mails)

        for message in mail.list_messages_by_id_json('me', mail_to_show):
            message_id = message['id']
            message_from = None
            message_title = None
            for header in message['payload']['headers']:
                if header['name'].lower() == 'from':
                    message_from = header['value']
                elif header['name'].lower() == 'subject':
                    message_title = header['value']

            messages.append({
                'id': message_id,
                'from': ''.join(message_from.split()[:-1]).strip('"'),
                'title': message_title
            })
        return Response(messages)

    @cred_check_decorator
    def post(self, request, **kwargs):
        mail = Gmail(creds=kwargs.get('credentials'))

        messages = []
        messages_ids_threads = mail.list_messages_matching_query(
            'me',
            count_messages=request.POST.get('count_messages', 5)
        )

        messages_id = list(map(lambda mes: mes['id'], messages_ids_threads))

        client_mails = UserViewedMail.objects.values_list('message_id')
        client_mails = list(map(lambda x: x[0], client_mails))
        mail_to_show = set(messages_id) - set(client_mails)

        for message in mail.list_messages_by_id_json('me', mail_to_show):
            message_id = message['id']
            message_from = None
            message_title = None
            for header in message['payload']['headers']:
                if header['name'].lower() == 'from':
                    message_from = header['value']
                elif header['name'].lower() == 'subject':
                    message_title = header['value']

            messages.append({
                'id': message_id,
                'from': ''.join(message_from.split()[:-1]).strip('"'),
                'title': message_title
            })
        return Response(messages)


class DetailPage(APIView):
    @cred_check_decorator
    def post(self, request, **kwargs):
        message_id = kwargs.get('message_id')

        UserViewedMail.objects.create(
            client_id=kwargs.get('credentials').client_id,
            message_id=message_id
        )

        mail = Gmail(creds=kwargs.get('credentials'))

        message_content = MailContent.objects.filter(message_id=message_id)

        if message_content.exists():
            message_html = message_content[0].content
        else:
            message_html = mail.list_messages_content(
                'me', [{'id': message_id, 'threadId': message_id}]
            )[0]

            MailContent.objects.create(
                message_id=message_id,
                content=message_html
            )

        return Response({'data': message_html})


class DeleteFromViewed(APIView):
    @cred_check_decorator
    def post(self, request, **kwargs):
        UserViewedMail.objects.filter(
            client_id=kwargs.get('credentials').client_id,
            message_id=kwargs.get('message_id')
        ).delete()

        return Response({'status': 'success'})


def authorize(request):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        settings.EMAIL['GMAIL']['CREDENTIALS'],
        scopes=settings.SCOPES
    )
    pre_domain = 'https' if request.is_secure() else 'http'

    flow.redirect_uri = (f"{pre_domain}://{request.get_host()}"
                         f"{reverse('auth_page:oauth2callback')}")

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        prompt='consent',
        include_granted_scopes='true'
    )
    request.session['state'] = state

    return HttpResponseRedirect(authorization_url)


def oauth2callback(request):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        settings.EMAIL['GMAIL']['CREDENTIALS'],
        scopes=settings.SCOPES,
        state=request.session['state']
    )

    pre_domain = 'https' if request.is_secure() else 'http'

    flow.redirect_uri = (f"{pre_domain}://{request.get_host()}"
                         f"{reverse('auth_page:oauth2callback')}")
    authorization_response = request.build_absolute_uri()
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials

    return JsonResponse({'credentials': credentials_to_dict(credentials)})


def revoke(request):
    if 'credentials' not in request.session:
        return ('You need to <a href="/authorize">authorize</a> '
                'before testing the code to revoke credentials.')

    credentials = google.oauth2.credentials.Credentials(
        **request.session['credentials']
    )

    revoke = requests.post(
        'https://accounts.google.com/o/oauth2/revoke',
        params={'token': credentials.token},
        headers={'content-type': 'application/x-www-form-urlencoded'}
    )

    status_code = getattr(revoke, 'status_code')

    if status_code == 200:
        return f'Credentials successfully revoked.{print_index_table()}'
    else:
        return f'An error occurred.{print_index_table()}'


def clear_credentials(request):
    if 'credentials' in request.session:
        del request.session['credentials']
    return HttpResponse(f'Credentials have been cleared.')


def credentials_to_dict(credentials):
    data = {
      "access_token": credentials.token,
      "client_id": credentials.client_id,
      "client_secret": credentials.client_secret,
      "refresh_token": credentials.refresh_token,
      "token_expiry": "2019-02-14T14:20:16Z",
      "token_uri": "https://www.googleapis.com/oauth2/v3/token",
      "user_agent": None,
      "revoke_uri": "https://oauth2.googleapis.com/revoke",
      "id_token": None,
      "id_token_jwt": None,
      "token_response": {
        "access_token": credentials.token,
        "expires_in": 3600,
        "scope": credentials.scopes[-1],
        "token_type": "Bearer"
      },
      "scopes": credentials.scopes,
      "token_info_uri": "https://oauth2.googleapis.com/tokeninfo",
      "invalid": False,
      "_class": "OAuth2Credentials",
      "_module": "oauth2client.client"
    }
    mail = Gmail(creds=google.oauth2.credentials.Credentials(
        token=data['access_token'],
        refresh_token=data['refresh_token'],
        token_uri="https://oauth2.googleapis.com/revoke",
        client_id=data['client_id'],
        client_secret=data['client_secret'],
        scopes=data['scopes'],
    ))
    email = mail.get_user_info('me')['emailAddress']
    try:
        creds = CredsContent.objects.get(email=email)
        creds.data = data
        creds.save()
    except CredsContent.DoesNotExist as _er:
        CredsContent.objects.create(email=email, data=data)
    return email


def print_index_table():
    return ('<table><tr><td><a href="/">'
            'Test an API request</a></td></tr></table>')
