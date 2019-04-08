import google.oauth2.credentials

from functools import wraps

from rest_framework.response import Response

from box.gmail.models import Gmail


def post_param_filter_decorator(*fields):
    def func_decorator(func):
        @wraps(func)
        def inner(self, request, *args, **kwargs):
            for field in fields:
                if field not in request.data:
                    return Response({'error': f'You must pass {field}'})
            return func(self, request, *args, **kwargs)
        return inner
    return func_decorator


def credentials_data_to_gmail(credentials_data, validate=False, owner=None, logger=None):
    # ToDo: replace all unusebly params & add docstring please
    credentials = google.oauth2.credentials.Credentials(**credentials_data)
    return Gmail(creds=credentials, owner=owner, logger=logger)
