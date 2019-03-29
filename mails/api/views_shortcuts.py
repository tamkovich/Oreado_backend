from django.http import Http404

from mails.models import Mail, MailSender

from functools import wraps


# # # Mail shortcuts

def mail_senders_decorator(func):
    @wraps(func)
    def inner(self, request, *args, **kwargs):
        mail_senders = MailSender.get_senders_name_for_user(user=request.user)
        resp = func(self, request, *args, **kwargs, mail_senders=mail_senders)
        return resp
    return inner


def get_mail_or_404(pk):
    try:
        return Mail.objects.get(id=pk)
    except Mail.DoesNotExist:
        raise Http404
