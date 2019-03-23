from oreado_backend.wsgi import application
from bs4 import BeautifulSoup
import pickle

from mails.models import Mail

from clean import clean_text_main, rec_tag, delete_extra_text

filename = 'finalized_model3.sav'

loaded_model = pickle.load(open(filename, 'rb'))

mails = Mail.objects.filter(category__isnull=True)

html_bodies = []

tags = {i: [] for i in range(len(mails))}

for ind, mail in enumerate(mails):
    html = clean_text_main(mail.html_body)

    html = '<div>' + html + '</div>'
    rec_tag(ind, BeautifulSoup(html, 'html.parser'), tags)
    html = tags[ind]

    html = delete_extra_text(html)

    html = ' '.join(html)
    html_bodies.append(html)

data = {}
predictions = loaded_model.predict(html_bodies)
print(len(predictions))
print(len(mails))
for mail, prediction in zip(mails, predictions):
    if prediction in data:
        data[prediction] += 1
    else:
        data[prediction] = 1
    print(prediction)

print(data)
