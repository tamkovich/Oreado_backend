import base64
import email
import loggers

from httplib2 import Http
from apiclient import errors
from googleapiclient.discovery import build
from oauth2client import file, client, tools

from utils.preproccessor import bytes_to_html
from oreado_dataset import settings


def my_decorator(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except errors.HttpError as _er:
            logger = args[0].__dict__.get('logger')
            if logger:
                loggers.log(logger=logger, level='ERROR', msg=f'method={func.__name__} An error occurred: {_er}')
    return wrapper


def for_all_methods(decorator):
    def decorate(cls):
        for attr in cls.__dict__: # there's propably a better way to do this
            if callable(getattr(cls, attr)):
                setattr(cls, attr, decorator(getattr(cls, attr)))
        return cls
    return decorate


@for_all_methods(my_decorator)
class Gmail:

    def __init__(self, creds=None, logger=None):
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        self.logger = logger
        if not creds:
            store = file.Storage(settings.EMAIL['GMAIL']['TOKEN'])
            creds = store.get()
            if not creds or creds.invalid:
                flow = client.flow_from_clientsecrets(settings.EMAIL['GMAIL']['CREDENTIALS'], settings.SCOPES)
                creds = tools.run_flow(flow, store)
            self.service = build('gmail', 'v1', http=creds.authorize(Http()))
        else:
            self.service = build(
                settings.API_SERVICE_NAME,
                settings.API_VERSION,
                credentials=creds
            )

    def list_labels(self, user_id, *args, **kwargs):
        """
        List all labels of the user's mailbox
        :param user_id: User's email address. The special value "me"
        :return: <list> List of Labels. Note that the
          returned list contains Labels IDs.
        """
        results = self.service.users().labels().list(userId=user_id, *args, **kwargs).execute()
        return results.get('labels', [])

    def list_messages_json(self, user_id, messages_ids, *args, **kwargs):
        """
        List Json Messages of the user's mailbox matching the receiving message id.
        :param user_id: User's email address. The special value "me"
        :param messages_ids: <list> list contains Message IDs
        :return: <list> List of Messages Json content.
        """
        return list(map(lambda m: self.get_message(user_id, m['id']), messages_ids, *args, **kwargs))

    def list_messages_by_id_json(self, user_id, messages_ids, *args, **kwargs):
        """
        List Json Messages by messages id.
        :param user_id: User's email address. The special value "me"
        :param messages_ids: <list> list contains Message IDs
        :return: <list> List of Messages Json content.
        """
        return list(map(lambda m: self.get_message(user_id, m), messages_ids, *args, **kwargs))

    def list_messages_content(self, user_id, messages_ids):
        """
        List Messages of the user's mailbox matching the receiving message id.
        :param user_id: User's email address. The special value "me"
        :param messages_ids: <list> list contains Message IDs,
        :return: <list> List of Messages content.
        """
        return list(map(lambda m: bytes_to_html(self.get_mime_message(user_id, m['id'])), messages_ids))

    def list_messages_matching_query(self, user_id, count_messages=None, query='', *args, **kwargs):
        """List all Messages of the user's mailbox matching the query.

        Args:
          user_id: User's email address. The special value "me"
          can be used to indicate the authenticated user.
          query: String used to filter messages returned.
          Eg.- 'from:user@some_domain.com' for Messages from a particular sender.

        Returns:
          List of Messages that match the criteria of the query. Note that the
          returned list contains Message IDs, you must use get with the
          appropriate ID to get the details of a Message.
        """
        response = self.service.users().messages().list(
            userId=user_id, maxResults=count_messages, q=query, *args, **kwargs
        ).execute()
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])
        while 'nextPageToken' in response:
            if count_messages and len(messages) >= count_messages:
                break
            page_token = response['nextPageToken']
            response = self.service.users().messages().list(
                userId=user_id, maxResults=count_messages, q=query, pageToken=page_token, *args, **kwargs
            ).execute()
            messages.extend(response['messages'])

        return messages[:count_messages] if count_messages else messages

    def list_messages_with_labels(self, user_id, label_ids=[], *args, **kwargs):
        """List all Messages of the user's mailbox with label_ids applied.

        Args:
          user_id: User's email address. The special value "me"
          can be used to indicate the authenticated user.
          label_ids: Only return Messages with these labelIds applied.

        Returns:
          List of Messages that have all required Labels applied. Note that the
          returned list contains Message IDs, you must use get with the
          appropriate id to get the details of a Message.
        """
        response = self.service.users().messages().list(
            userId=user_id, labelIds=label_ids, *args, **kwargs
        ).execute()
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])

        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = self.service.users().messages().list(
                userId=user_id, labelIds=label_ids, pageToken=page_token, *args, **kwargs
            ).execute()
            messages.extend(response['messages'])

        return messages

    def get_message(self, user_id, msg_id):
        """Get a Message with given ID.

        Args:
          user_id: User's email address. The special value "me"
          can be used to indicate the authenticated user.
          msg_id: The ID of the Message required.

        Returns:
          A Message.
        """
        message = self.service.users().messages().get(userId=user_id, id=msg_id).execute()

        loggers.log(logger=self.logger, level='INFO', msg=f'Message snippet: {message["snippet"]}')

        return message

    def get_mime_message(self, user_id, msg_id):
        """Get a Message and use it to create a MIME Message.

        Args:
          user_id: User's email address. The special value "me"
          can be used to indicate the authenticated user.
          msg_id: The ID of the Message required.

        Returns:
          A MIME Message, consisting of data from Message.
        """
        message = self.service.users().messages().get(
            userId=user_id,
            id=msg_id,
            format='raw'
        ).execute()

        loggers.log(logger=self.logger, level='INFO', msg=message['labelIds'])
        msg_str = base64.urlsafe_b64decode(message['raw']).decode('utf-8')

        mime_msg = email.message_from_string(msg_str)

        if mime_msg.is_multipart():
            for part in mime_msg.walk():
                ctype = part.get_content_type()
                cdispo = str(part.get('text/html'))
                if ctype == 'text/html' and 'attachment' not in cdispo:
                    body = part.get_payload(decode=True)
                    return body
        return mime_msg.get_payload()
