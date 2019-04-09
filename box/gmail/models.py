import loggers
import base64
import email
import time

import google.auth.exceptions

from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.conf import settings

from oauth2client import file, client, tools
from googleapiclient.discovery import build
from apiclient import errors
from httplib2 import Http

from mails.models import Mail, Credential
from utils.preproccessor import (
    bytes_to_html,
    bytes_html_to_text,
    scrap_mail_from_text,
)


User = get_user_model()


def my_decorator(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except errors.HttpError as _er:
            logger = args[0].__dict__.get("logger")
            if logger:
                loggers.log(
                    logger=logger,
                    level="ERROR",
                    msg=f"method={func.__name__} An error occurred: {_er}",
                )

    return wrapper


def for_all_methods(decorator):
    def decorate(cls):
        for attr in cls.__dict__:  # there's propably a better way to do this
            if callable(getattr(cls, attr)):
                setattr(cls, attr, decorator(getattr(cls, attr)))
        return cls

    return decorate


@for_all_methods(my_decorator)
class Gmail:
    def __init__(self, creds=None, owner=None, logger=None):
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        self.data = {}

        self.logger = logger
        if not creds:
            store = file.Storage(settings.EMAIL["GMAIL"]["TOKEN"])
            creds = store.get()
            if not creds or creds.invalid:
                flow = client.flow_from_clientsecrets(
                    settings.EMAIL["GMAIL"]["CREDENTIALS"], settings.SCOPES
                )
                creds = tools.run_flow(flow, store)
            self.service = build("gmail", "v1", http=creds.authorize(Http()))
        else:
            self.service = build(
                settings.API_SERVICE_NAME, settings.API_VERSION, credentials=creds
            )

        loggers.log(
            logger=self.logger,
            level="INFO",
            msg="Just initialized"
        )
        self.owner = owner
        self.messages = []
        self.html_messages = []
        self.common_data = []

    def validate_credentials(self):
        try:
            resp = self.service.users().getProfile(userId='me').execute()
            return True
        except google.auth.exceptions.RefreshError as err:
            return False

    def list_labels(self, user_id, *args, **kwargs):
        """
        List all labels of the user's mailbox
        :param user_id: User's email address. The special value "me"
        :return: <list> List of Labels. Note that the
          returned list contains Labels IDs.
        """
        results = (
            self.service.users()
            .labels()
            .list(userId=user_id, *args, **kwargs)
            .execute()
        )
        return results.get("labels", [])

    def list_messages_json(self, user_id, messages_ids, *args, **kwargs):
        """
        List Json Messages of the user's mailbox matching the receiving message id.
        :param user_id: User's email address. The special value "me"
        :param messages_ids: <list> list contains Message IDs
        :return: <list> List of Messages Json content.
        """
        return list(
            map(
                lambda m: self.get_message(user_id, m["id"]),
                messages_ids,
                *args,
                **kwargs,
            )
        )

    def list_messages_by_id_json(self, user_id, messages_ids, *args, **kwargs):
        """
        List Json Messages by messages id.
        :param user_id: User's email address. The special value "me"
        :param messages_ids: <list> list contains Message IDs
        :return: <list> List of Messages Json content.
        """
        return list(
            map(lambda m: self.get_message(user_id, m), messages_ids, *args, **kwargs)
        )

    def list_messages_content(self, user_id, messages_ids):
        """
        List Messages of the user's mailbox matching the receiving message id.
        :param user_id: User's email address. The special value "me"
        :param messages_ids: <list> list contains Message IDs,
        :return: <list> List of Messages content.
        """
        return list(
            map(
                lambda m: bytes_to_html(self.get_mime_message(user_id, m["id"])),
                messages_ids,
            )
        )

    def list_messages_common_data(
            self,
            user_id,
            messages_ids,
    ):
        a_week_ago = datetime.now() - timedelta(days=7)
        need_more = True
        count = 0
        for m in messages_ids:
            if Mail.objects.filter(message_id=m["id"]).exists():
                continue
            if not need_more:
                break
            message = self.get_message(user_id, m["id"])
            body = self.get_mime_message(user_id, m["id"])
            html_body = bytes_to_html(body)
            text_body = bytes_html_to_text(body)
            res = {"message_id": m["id"], "snippet": message["snippet"]}
            res["html_body"] = html_body
            res["text_body"] = text_body
            for d in message["payload"]["headers"]:
                if d["name"] == "Date":
                    res["date"] = d["value"]
                    data = d["value"].split(',')
                    if len(data) == 1:
                        data = data[0].strip()
                    else:
                        data = data[1].strip()
                    cleaned = ' '.join(data.split()[:4])
                    res["cleaned_date"] = datetime.strptime(
                        cleaned,
                        '%d %b %Y %H:%M:%S'
                    )
                    if res["cleaned_date"] < a_week_ago:
                        need_more = False
                        break
                if d["name"] == "From":
                    res["come_from"] = d["value"]
                    res["come_from_email"] = scrap_mail_from_text(d["value"])
                if d["name"] == "To":
                    res["go_to"] = d["value"]
                    res["go_to_email"] = scrap_mail_from_text(d["value"])
            else:
                count += 1
                if isinstance(self.owner, int):
                    res["owner_id"]
                elif isinstance(self.owner, Credential):
                    res["owner_id"] = self.owner.id
                Mail.objects.create(**res)
                self.messages.append(message)
                self.html_messages.append(text_body)
                self.common_data.append(res)
        if count == 0:
            return False
        return need_more

    def get_message_process(self, request_id, response, exception):
        if request_id in self.data:
            self.data[request_id][0] = response
        else:
            self.data[request_id] = [response, None]

        loggers.log(
            logger=self.logger,
            level="INFO",
            msg=f'Message: {response}',
        )
        return response

    def get_mime_message_process(self, request_id, response, exception):
        request_id = str(int(request_id) - 1)

        if not response:
            return

        loggers.log(logger=self.logger, level="INFO", msg=response["labelIds"])
        try:
            msg_str = base64.urlsafe_b64decode(response["raw"]).decode("utf-8")
        except (UnicodeError, UnicodeDecodeError, UnicodeEncodeError) as _er:
            loggers.log(
                logger=self.logger,
                level="ERROR",
                msg=f"method=get_mime_message An error occurred: {_er}",
            )

            msg_str = ''
        mime_msg = email.message_from_string(msg_str)

        if mime_msg.is_multipart():
            for part in mime_msg.walk():
                ctype = part.get_content_type()
                cdispo = str(part.get("text/html"))
                if ctype == "text/html" and "attachment" not in cdispo:
                    body = part.get_payload(decode=True)
                    if request_id in self.data:
                        self.data[request_id][1] = body
                    else:
                        self.data[request_id] = [None, body]
                    return body

        if request_id in self.data:
            self.data[request_id][1] = mime_msg.get_payload()
        else:
            self.data[request_id] = [None, mime_msg.get_payload()]
        return mime_msg.get_payload()

    def list_messages_common_data_by_user_id(self, user_id, messages_ids):
        a_week_ago = datetime.now() - timedelta(days=10)
        count = 0

        need_more = True

        batch = self.service.new_batch_http_request()

        for m in messages_ids:
            if Mail.objects.filter(message_id=m["id"]).exists():
                continue
            if not need_more:
                break
            batch.add(self.service.users().messages().get(userId=user_id, id=m['id']), callback=self.get_message_process)
            batch.add(self.service.users().messages().get(userId=user_id, id=m['id'], format="raw"), callback=self.get_mime_message_process)

        batch.execute(http=self.service._http)

        for ind, (key, value) in enumerate(self.data.items()):
            message = value[0]
            body = value[1]

            if not message or not body:
                continue

            html_body = bytes_to_html(body)
            text_body = bytes_html_to_text(body)
            res = {"message_id": messages_ids[ind]["id"], "snippet": message["snippet"]}
            res["html_body"] = html_body
            res["text_body"] = text_body.replace('=20', '').replace('=A0', '').replace('=0A', '').replace('=0D', '')  # =20 and =A0 specific symbols in mails
            for d in message["payload"]["headers"]:
                if d["name"] == "Date":
                    res["date"] = d["value"]
                    data = d["value"].split(',')
                    if len(data) == 1:
                        data = data[0].strip()
                    else:
                        data = data[1].strip()
                    cleaned = ' '.join(data.split()[:4])
                    res["cleaned_date"] = datetime.strptime(
                        cleaned,
                        '%d %b %Y %H:%M:%S'
                    )
                    if res["cleaned_date"] < a_week_ago:
                        need_more = False
                        break
                if d["name"] == "From":
                    res["come_from"] = d["value"]
                    res["come_from_email"] = scrap_mail_from_text(d["value"])
                if d["name"] == "To":
                    res["go_to"] = d["value"]
                    res["go_to_email"] = scrap_mail_from_text(d["value"])
                if d["name"] == "Subject":
                    res["go_to"] = d["value"]
                    res["go_to_email"] = d["value"]
            else:
                count += 1
                res["owner_id"] = (self.owner if isinstance(self.owner, int)
                                   else self.owner.id)

                self.messages.append(message)
                self.html_messages.append(text_body)
                self.common_data.append(res)

                message_id = res['message_id']
                del res['message_id']
                Mail.objects.get_or_create(
                    message_id=message_id, defaults=res
                )

        self.data = {}
        if count == 0:
            return False
        return need_more

    def list_messages_one_step(self, user_id, count_messages=None):
        iteration = 0
        page_token = None
        need_more = True

        start = time.time()

        loggers.log(
            logger=self.logger,
            level="INFO",
            msg='START',
        )

        while True and need_more:
            if iteration > 0:
                count_messages += 100
            messages_ids, page_token = self.list_messages_matching_query(
                user_id,
                count_messages=count_messages,
                page_token=page_token,
            )
            need_more = self.list_messages_common_data_by_user_id(
                user_id,
                messages_ids[count_messages-100:] if iteration > 0 else messages_ids,
            )
            iteration += 1

        loggers.log(
            logger=self.logger,
            level="INFO",
            msg=f'END {time.time()-start}',
        )

    def list_messages_matching_query(
        self, user_id, count_messages=None, query="", page_token=None, *args, **kwargs
    ):
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
        if page_token:
            response = (
                self.service.users()
                    .messages()
                    .list(
                    userId=user_id,
                    maxResults=count_messages,
                    q=query,
                    pageToken=page_token,
                    *args,
                    **kwargs,
                ).execute()
            )
        else:
            response = (
                self.service.users()
                .messages()
                .list(userId=user_id, maxResults=count_messages, q=query, *args, **kwargs)
                .execute()
            )
        messages = []
        if "messages" in response:
            messages.extend(response["messages"])
        while "nextPageToken" in response:
            if count_messages and len(messages) >= count_messages:
                break
            page_token = response["nextPageToken"]
            response = (
                self.service.users()
                .messages()
                .list(
                    userId=user_id,
                    maxResults=count_messages,
                    q=query,
                    pageToken=response["nextPageToken"],
                    *args,
                    **kwargs,
                )
                .execute()
            )
            messages.extend(response["messages"])
        if "nextPageToken" not in response:
            return messages, None
        if count_messages:
            return messages[:count_messages], page_token
        return messages, page_token

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
        response = (
            self.service.users()
            .messages()
            .list(userId=user_id, labelIds=label_ids, *args, **kwargs)
            .execute()
        )
        messages = []
        if "messages" in response:
            messages.extend(response["messages"])

        while "nextPageToken" in response:
            page_token = response["nextPageToken"]
            response = (
                self.service.users()
                .messages()
                .list(
                    userId=user_id,
                    labelIds=label_ids,
                    pageToken=page_token,
                    *args,
                    **kwargs,
                )
                .execute()
            )
            messages.extend(response["messages"])

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

        message = (
            self.service.users().messages().get(userId=user_id, id=msg_id).execute()
        )
        loggers.log(
            logger=self.logger,
            level="INFO",
            msg=f'Message snippet: {message["snippet"]}',
        )

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
        message = (
            self.service.users()
            .messages()
            .get(userId=user_id, id=msg_id, format="raw")
            .execute()
        )
        loggers.log(logger=self.logger, level="INFO", msg=message["labelIds"])
        try:
            msg_str = base64.urlsafe_b64decode(message["raw"]).decode("utf-8")
        except (UnicodeError, UnicodeDecodeError, UnicodeEncodeError) as _er:
            loggers.log(
                logger=self.logger,
                level="INFO",
                msg=message["raw"]
            )
            loggers.log(
                logger=self.logger,
                level="ERROR",
                msg=f"method=get_mime_message An error occurred: {_er}",
            )

            msg_str = ''
        mime_msg = email.message_from_string(msg_str)

        if mime_msg.is_multipart():
            for part in mime_msg.walk():
                ctype = part.get_content_type()
                cdispo = str(part.get("text/html"))
                if ctype == "text/html" and "attachment" not in cdispo:
                    body = part.get_payload(decode=True)
                    return body
        return mime_msg.get_payload()

    def get_user_info(self, user_id):
        data = self.service.users().getProfile(userId=user_id)
        return data.execute()
