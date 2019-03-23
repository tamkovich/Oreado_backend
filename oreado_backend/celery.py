import os
import google.oauth2.credentials

from celery import Celery

from oreado_backend.wsgi import application
from auth_page.models import Credential
from box.gmail.models import Gmail

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "oreado_backend.settings")

app = Celery("oreado_backend")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print("Request: {0!r}".format(self.request))


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls load_mails() every 10 minutes.
    sender.add_periodic_task(600.0, load_mails.s())


@app.task
def load_mails():
    credentials = Credential.objects.all()
    for cred in credentials:
        mail = Gmail(
            creds=google.oauth2.credentials.Credentials(**cred.credentials),
            owner=cred
        )
        messages_ids = mail.list_messages_matching_query("me", count_messages=200)
        mail.list_messages_common_data("me", messages_ids[:200])


if __name__ == "__main__":
    app.start()
