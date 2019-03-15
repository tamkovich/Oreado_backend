import uuid
import requests

import google.oauth2.credentials
import google_auth_oauthlib.flow

from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.sites.models import Site

from auth_page.models import Credential
from box.gmail.models import Gmail


def authorize(request):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        settings.EMAIL['GMAIL']['CREDENTIALS'],
        scopes=settings.SCOPES
    )
    pre_domain = 'https' if request.is_secure() else 'http'
    
    current_site = Site.objects.get_current()
    flow.redirect_uri = (f"{pre_domain}://{current_site.domain}"
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
        state=request.session.get('state') or request.GET.get('state'),
    )

    pre_domain = 'https' if request.is_secure() else 'http'

    current_site = Site.objects.get_current()
    flow.redirect_uri = (f"{pre_domain}://{current_site.domain}"
                         f"{reverse('auth_page:oauth2callback')}")
    authorization_response = request.build_absolute_uri()
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    _ = save_credentials(credentials)
    return redirect(reverse('api-mails:list'))


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


def save_credentials(credentials):
    data = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    mail = Gmail(creds=google.oauth2.credentials.Credentials(**data))
    email = mail.get_user_info('me')['emailAddress']
    try:
        creds = Credential.objects.get(email=email)
        creds.data = data
        creds.save()
    except Credential.DoesNotExist as _er:
        Credential.objects.create(
            email=email,
            data=data,
            uuid_token=uuid.uuid4()
        )
    return email


def print_index_table():
    return ('<table><tr><td><a href="/">'
            'Test an API request</a></td></tr></table>')
