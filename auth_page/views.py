import json
import requests

import google.oauth2.credentials
import google_auth_oauthlib.flow
from oauth2client import client

from functools import wraps

from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from auth_page.models import CredsContent, GmailMails
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
    _ = credentials_to_dict(credentials)
    return redirect(reverse('auth_page:home'))


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


def home(request):
    return render(request, 'auth/home.html', {'mail': GmailMails.objects.random()})
