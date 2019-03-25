import os

from box.gmail.models import Gmail
from box.gmail.dataset import DatasetGmail


def prepare_gmail():
    mail = Gmail()
    messages_ids = mail.list_messages_matching_query("me")
    messages = mail.list_messages_json("me", messages_ids)

    dataset = DatasetGmail(messages)
    dataset.headers(os.path.join("datasets", "gmail_dataset.csv"))
