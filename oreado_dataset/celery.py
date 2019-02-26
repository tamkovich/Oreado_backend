import os
import google.oauth2.credentials

from celery import Celery

from oreado_dataset.wsgi import application
from auth_page.models import CredsContent
from box.gmail.models import Gmail

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oreado_dataset.settings')

app = Celery('oreado_dataset')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls load_mails() every 5 minutes.
    sender.add_periodic_task(300.0, load_mails.s())


@app.task
def load_mails():
    credentials = CredsContent.objects.all()
    for creds in credentials:
        mail = Gmail(
            creds=google.oauth2.credentials.Credentials(
                token=creds.data['access_token'],
                refresh_token=creds.data['refresh_token'],
                token_uri="https://oauth2.googleapis.com/revoke",
                client_id=creds.data['client_id'],
                client_secret=creds.data['client_secret'],
                scopes=creds.data['scopes'],
            ),
            owner=creds
        )
        messages_ids = mail.list_messages_matching_query('me', count_messages=5)
        mail.list_messages_common_data('me', messages_ids[:3])


if __name__ == '__main__':
    app.start()
