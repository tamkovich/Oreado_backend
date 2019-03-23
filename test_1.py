from oreado_backend.wsgi import application

import pickle

from mails.models import Mail


filename = 'finalized_model2.sav'

loaded_model = pickle.load(open(filename, 'rb'))

mails = Mail.objects.filter(category__isnull=True)

html_bodies = []

for mail in mails:
    html_bodies.append(mail.html_body)
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