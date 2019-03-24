from oreado_backend.wsgi import application

import os
import pickle

import google.oauth2.credentials

from datetime import datetime

from django.contrib.auth import get_user_model

from bs4 import BeautifulSoup
from celery import Celery

from auth_page.models import Credential
from mails.models import MailSender
from box.gmail.models import Gmail
from mails.models import Mail
from clean import clean_text_main, rec_tag, delete_extra_text


User = get_user_model()

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


MODEL_FILENAME = 'finalized_model3.sav'
loaded_model = pickle.load(open(MODEL_FILENAME, 'rb'))

NEWS_DIGEST_ID = 3
INFO_MESSAGE_ID = 3


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


@app.task
def classify_mail_category():
    mails = Mail.objects.filter(category__isnull=True)

    html_bodies = []

    tags = {i: [] for i in range(len(mails))}

    for ind, mail in enumerate(mails):
        html = '<div>' + clean_text_main(mail.html_body) + '</div>'
        rec_tag(ind, BeautifulSoup(html, 'html.parser'), tags)

        html = delete_extra_text(tags[ind])
        html_bodies.append(' '.join(html))

    predictions = loaded_model.predict(html_bodies)

    for mail, prediction in zip(mails, predictions):
        mail.category_id = prediction
        mail.save()


@app.task
def add_cleaned_data_to_mail():
    for mail in Mail.objects.all():
        if not mail.cleaned_date:
            mail.cleaned_date = datetime.strptime(
                mail.date.split(',')[1].strip().split('+')[0].strip(),
                '%d %b %Y %H:%M:%S'
            )
            mail.save()


@app.task
def mail_sender_active():
    DATA = {}

    all_users = User.objects.all()
    all_mails = Mail.objects.all()

    mails_to_classify = []

    for mail in all_mails:
        if mail.category is None:
            mails_to_classify.append(mail)

    html_bodies = []

    tags = {i: [] for i in range(len(mails_to_classify))}

    for ind, mail in enumerate(mails_to_classify):
        html = '<div>' + clean_text_main(mail.html_body) + '</div>'
        rec_tag(ind, BeautifulSoup(html, 'html.parser'), tags)

        html = delete_extra_text(tags[ind])
        html_bodies.append(' '.join(html))

    if len(html_bodies):
        predictions = loaded_model.predict(html_bodies)

        for mail, prediction in zip(mails_to_classify, predictions):
            mail.category_id = prediction
            mail.save()

    for user in all_users:
        for mail in all_mails:
            if f"{user.id}-{mail.come_from}" in DATA:
                DATA[f"{user.id}-{mail.come_from}"].append(mail.category_id)
            else:
                DATA[f"{user.id}-{mail.come_from}"] = []

    for key, value in DATA.items():
        if not len(value):
            continue
        digest_percent = value.count(NEWS_DIGEST_ID) / len(value)
        info_percent = value.count(INFO_MESSAGE_ID) / len(value)

        average = (digest_percent + info_percent) / 2

        MailSender.objects.update_or_create(
            name=key.split('-')[1], user_id=key.split('-')[0],
            defaults={
                'is_active': True if average >= 0.5 else False,
                'average': average,
                'mail_count': len(value)
            }
        )


if __name__ == "__main__":
    app.start()
