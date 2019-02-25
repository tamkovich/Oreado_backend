import os

from box.gmail.models import Gmail

mail = Gmail()


def test_labels():
    return mail.list_labels('me')


def test_messages_id():
    return mail.list_messages_matching_query('me')


def test_labels_messages_id():
    return mail.list_messages_with_labels('me', label_ids=['CATEGORY_PERSONAL'])


def test_messages_content():
    messages = mail.list_messages_matching_query('me')
    html_messages = mail.list_messages_content('me', messages)
    for i, html in enumerate(html_messages):
       with open(os.path.join('test', f'{i}.html'), 'w') as f:
           f.write(str(html))


if __name__ == '__main__':
    print(test_messages_content())
