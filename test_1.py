from oreado_backend.wsgi import application

import pickle

from django.contrib.auth import get_user_model

from bs4 import BeautifulSoup

from clean import clean_text_main, rec_tag, delete_extra_text
from mails.models import MailSender
from mails.models import Mail


User = get_user_model()


DATA = {}

MODEL_FILENAME = 'finalized_model3.sav'
loaded_model = pickle.load(open(MODEL_FILENAME, 'rb'))

NEWS_DIGEST_ID = 3
INFO_MESSAGE_ID = 3

all_users = User.objects.all()
all_mails = Mail.objects.all()

mails_to_classify = []

for user in all_users:
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
    digest_percent = value.count(NEWS_DIGEST_ID) / len(value)
    info_percent = value.count(INFO_MESSAGE_ID) / len(value)

    average = (digest_percent + info_percent) / 2

    mail_sender = MailSender.objects.get_or_create(
        name=key.split('-')[1], user_id=key.split('-')[0],
        defaults={'is_active': True if average >= 0.5 else False}
    )
