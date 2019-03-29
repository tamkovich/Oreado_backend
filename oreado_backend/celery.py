from oreado_backend.wsgi import application

import os
import re
import pickle

from datetime import datetime

from django.contrib.auth import get_user_model

from celery import Celery

from shortcuts.shortcuts import credentials_data_to_gmail
from auth_page.models import Credential
from mails.models import MailSender
from mails.models import Mail


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


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls load_mails() every 10 minutes.
    sender.add_periodic_task(600.0, load_mails.s())


@app.task
def load_mails():
    credentials = Credential.objects.all()
    for cred in credentials:
        try:
            mail = credentials_data_to_gmail(**cred.credentials)
            mail.list_messages_one_step("me", count_messages=100)
        except Exception as err:
            print(err)


@app.task
def load_mails_for_user(credentials_data, cred_id, user_id):
    mail = credentials_data_to_gmail(credentials_data, owner=cred_id)

    mail.list_messages_one_step("me", count_messages=100)
    mail_sender_active_by_user_id.delay(user_id)


@app.task
def mail_sender_active_by_user_id(user_id):
    DATA = {}

    user = User.objects.get(id=user_id)
    all_mails = Mail.objects.filter(owner__user=user)

    html_bodies = []

    mail_senders = MailSender.objects.filter(user=user, is_active=True)
    for mail_sender in mail_senders:
        mail_sender.is_active = False
        mail_sender.save()

    for ind, mail in enumerate(all_mails):
        html = ''.join(
            re.findall(r'</?[a-z]\w*\b|>', mail.html_body, flags=re.I | re.M)
        )
        html_bodies.append(html)

    if len(html_bodies):
        predictions = loaded_model.predict(html_bodies)

        for mail, prediction in zip(all_mails, predictions):
            mail.category_id = prediction
            mail.save()

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
            name='-'.join(key.split('-')[1:]), user_id=key.split('-')[0],
            defaults={
                'is_active': True if average >= 0.5 else False,
                'average': average,
                'mail_count': len(value)
            }
        )
    return


@app.task
def add_cleaned_data_to_mail():
    for mail in Mail.objects.all():
        if not mail.cleaned_date:
            data = mail.date.split(',')
            if len(data) == 1:
                data = data[0].strip()
            else:
                data = data[1].strip()
            cleaned = ' '.join(data.split()[:4])
            mail.cleaned_date = datetime.strptime(
                cleaned,
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

    for ind, mail in enumerate(mails_to_classify):
        html = (''.join(
            re.findall(r'</?[a-z]\w*\b|>', mail.html_body, flags=re.I | re.M))
                .replace('<', '').replace('>', ' ').replace('/', ''))
        html_bodies.append(html)

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

