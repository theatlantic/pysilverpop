import inspect

from requests_oauthlib import OAuth2Session

from .utils import replace_in_nested_mapping, map_to_xml

class api_method(object):
    """
    The `api_method` decorator tries to simplify declaring most of the methods
    in the API wrapper. The majority of the methods in the Silverpop API have a
    simple XML tag/value system and repeating the logic across a thousand lines
    is gonna cause problems.
    """

    def __init__(self, cmd_name, definition=()):
        self.cmd_name = cmd_name
        self.definition = definition

    def __call__(self, func):
        outer_self = self
        argspec = inspect.getargspec(func)

        def wrapper(self, *args, **kwargs):
            # Name the args via zip and then put them in the kwargs.
            values = zip(argspec.args[1:], args)
            kwargs.update(values)
            tree = outer_self._build_tree(**kwargs)
            return self._call(tree)

        # Preserve the argument signature of the wrapped function.
        # fullargspec preserves the defaults while argspec does not.
        full_argspec = inspect.formatargspec(*argspec)
        non_default_argspec = inspect.formatargspec(argspec.args)

        new_func = ("def %s%s:\n"
                    "    return wrapper%s" % (func.__name__, full_argspec, non_default_argspec))
        exec_scope = {"wrapper": wrapper, }

        # Execute the signature-preserving wrapper function in a dict-based
        # closure and return it.
        exec new_func in exec_scope
        return exec_scope[func.__name__]

    def _build_tree(self, **kwargs):
        definition = replace_in_nested_mapping(self.definition, kwargs)
        return map_to_xml(definition, command=self.cmd_name)


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
        ("MailingId", "mailingId"),
        ("RecipientEmail", "recipientEmail"),))
    def send_mailing(self, mailingId, recipientEmail):
        pass

    @api_method("ScheduleMailing", definition=(
        ("TEMPLATE_ID", "template_id"),
        ("LIST_ID", "list_id"),
        ("MAILING_NAME", "mailing_name"),
        ("SEND_HTML", "send_html"),
        ("SEND_TEXT", "send_text"),
        ("SUBJECT", "subject"),
        ("FROM_NAME", "from_name"),
        ("FROM_ADDRESS", "from_address"),
        ("REPLY_TO", "reply_to"),
        ("VISIBILITY", "shared"),
        ("SCHEDULED", "scheduled"),
        ("INBOX_MONITOR", "inbox_monitor"),
        ("SEND_TIME_OPTIMIZATION", "send_time_optimization"),
        ("WA_MAILINGLEVEL_CODE", "wa_mailinglevel_code"),
        ("SUPPRESSION_LISTS", (
            ("SUPPRESSION_LIST_ID", "suppression_lists"),)),
        ("PARENT_FOLDER_PATH", "parent_folder_path"),
        ("CREATE_PARENT_FOLDER", "create_parent_folder"),
        ("CUSTOM_OPT_OUT", "custom_opt_out"),
        ("SUBSTITUTIONS", (
            ("SUBSTITUTION", "substitutions"),)),
        ))
    def schedule_mailing(self, template_id, list_id, mailing_name,
            send_html=False, send_text=False, subject=None, from_name=None,
            from_address=None, reply_to=None, shared=True, scheduled=None,
            inbox_monitor=None, send_time_optimization=None,
            wa_mailinglevel_code=None, suppression_lists=None,
            parent_folder_path=None, create_parent_folder=None,
            custom_opt_out=None, substitutions=None):
        pass
