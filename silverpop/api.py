import inspect
from xml.etree import ElementTree

from requests_oauthlib import OAuth2Session

class api_method(object):
    def __init__(self, cmd_name, definition=()):
        self.cmd_name = cmd_name
        self.definition = definition

    def __call__(self, func):
        outer_self = self

        def wrapper(self, *args, **kwargs):
            values = zip(outer_self.definition, args)
            kwargs.update(values)
            tree = outer_self._build_tree(**kwargs)
            self._call(tree)

        # Preserve the argument signature of the wrapped function.
        # fullargspec preserves the defaults while argspec does not.
        full_argspec = inspect.formatargspec(*inspect.getargspec(func))
        non_default_argspec = inspect.formatargspec(inspect.getargspec(func)[0])

        new_func = ("def %s%s:\n"
                    "    return wrapper%s" % (func.__name__, full_argspec, non_default_argspec))
        exec_scope = {"wrapper": wrapper, }

        # Execute the signature-preserving wrapper function in a dict-based
        # closure and return it.
        exec new_func in exec_scope
        return exec_scope[func.__name__]

    def _build_tree(self, **kwargs):
        # The base form of the call is <Envelope><Body><CommandName></CommandName></Body></Envelope>
        envelope = ElementTree.Element("Envelope")

        body = ElementTree.Element("Body")
        envelope.append(body)

        command = ElementTree.Element(self.cmd_name)
        body.append(command)

        # Iterate over scope definitions.
        for kwarg_key, tag_name in self.definition:
            element = ElementTree.Element(tag_name)
            value = kwargs[kwarg_key]

            # Boolean flags do not need text content.
            if type(value) != bool:
                element.text = str(value)

            if value:
                command.append(element)

        return ElementTree.tostring(envelope)


class Silverpop(object):
    oauth_endpoint = "https://api%s.ibmmarketingcloud.com/oauth/token"
    api_endpoint = "https://api%s.ibmmarketingcloud.com/XMLAPI"

    def __init__(self, client_id, client_secret, refresh_token, server_number=5):
        self.oauth_endpoint = self.oauth_endpoint % server_number
        self.api_endpoint = self.api_endpoint % server_number

        refresh_kwargs = {
            "client_id": client_id,
            "client_secret": client_secret
        }

        # We need to pass a fake access token because Silverpop's OAuth system
        # skips the initial access token grant but oauthlib raises an exception
        # if "access_token".
        self.token = {
            "expires_in": "-30",
            "access_token": "None",
            "refresh_token": refresh_token,
        }

        def token_updater(token):
            self.token = token

        # Build our session and assign it to an instance variable.
        self.session = OAuth2Session(auto_refresh_kwargs=refresh_kwargs,
                auto_refresh_url=self.oauth_endpoint,
                token_updater=token_updater,
                token=self.token)

    def _call(self, xml):
        return self.session.post(self.api_endpoint, data={"xml": xml})

    @api_method("ScheduleMailing", definition=(
        ("mailingId", "MailingId"),
        ("recipientEmail", "RecipientEmail"),))
    def send_mailing(self, mailingId, recipientEmail):
        pass

    @api_method("ScheduleMailing", definition=(
        ("template_id", "TEMPLATE_ID"),
        ("list_id", "LIST_ID"),
        ("mailing_name", "MAILING_NAME"),
        ("send_html", "SEND_HTML"),))
    def schedule_mailing(self, template_id, list_id, mailing_name, send_html=True):
        pass
