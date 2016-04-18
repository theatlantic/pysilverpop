import inspect
import logging
from xml.etree import ElementTree

from requests_oauthlib import OAuth2Session

from .utils import replace_in_nested_mapping, map_to_xml

logger = logging.getLogger(__name__)


class api_method(object):
    """
    :param str cmd_name: The name of the XML method in the Silverpop API.
    :param tuple definition: The signature of the API method.

    The `api_method` decorator tries to simplify declaring most of the methods
    in the API wrapper. The majority of the methods in the Silverpop API have a
    simple XML tag/value system and repeating the logic across a thousand lines
    is gonna cause problems.

    The API is SOAP-like but does not use SOAP namespacing or SOAP discovery.

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
        new_func = exec_scope[func.__name__]
        new_func.__doc__ = self.build_doc(func)
        return new_func

    def build_doc(self, func=None):
        return ":API Method: %s\n%s\n" % (self.cmd_name, func.__doc__ or "")

    def _build_tree(self, **kwargs):
        definition = replace_in_nested_mapping(self.definition, kwargs)
        return map_to_xml(definition, command=self.cmd_name)


class Silverpop(object):
    """
    :param str client_id: Silverpop OAuth client id.
    :param str client_secret: Silverpop OAuth client secret.
    :param str refresh_token: Silverpop OAuth refersh token.
    :param int server_number: Silverpop auth server number. Interpolated into API subdomain.

    .. note::

        Silverpop uses a modified OAuth 2 system that uses a refresh token to
        retrieve an access token, even for the first grant. Generally, OAuth 2
        grants an access token and a refresh token initially.
    """
    oauth_endpoint = "https://api%s.ibmmarketingcloud.com/oauth/token"
    api_endpoint = "https://api%s.ibmmarketingcloud.com/XMLAPI"

    def __init__(self, client_id, client_secret, refresh_token, server_number):
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
        logger.debug("Request: %s" % xml)
        response = self.session.post(self.api_endpoint, data={"xml": xml})
        return ApiResponse(response)

    @api_method("SendMailing", definition=(
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

    @api_method("AddRecipient", definition=(
        ("LIST_ID", "list_id"),
        ("CREATED_FROM", "created_from"),
        ("SEND_AUTOREPLY", "send_autoreply"),
        ("UPDATE_IF_FOUND", "update_if_found"),
        ("ALLOW_HTML", "allow_html"),
        ("VISITOR_KEY", "visitor_key"),
        ("CONTACT_LISTS", (
            ("CONTACT_LIST", "contact_lists"),)),
        ("HONOR_OPTOUT_STATUS", "honor_optout_status"),
        ("SYNC_FIELDS", (
            ("SYNC_FIELD", "sync_fields"),)),
        ("COLUMN", "columns"),
        ))
    def add_recipient(self, list_id, created_from, send_autoreply=False,
            update_if_found=False, allow_html=False, visitor_key=None,
            contact_lists=None, honor_optout_status=False, sync_fields=None,
            columns=None):
        pass


    @api_method("SaveMailing", definition=(
        ("Header", (
            ("MailingName", "mailing_name"),
            ("MailingID", "mailing_id"),
            ("Subject", "subject"),
            ("ListID", "list_id"),
            ("FromName", "from_name"),
            ("FromAddress", "from_address"),
            ("ReplyTo", "reply_to"),
            ("Visibility", "shared"),
            ("FolderPath", "folder_path"),
            ("Encoding", "encoding"),
            ("TrackingLevel", "tracking_level"),
            ("ClickHereMessage", "click_here_message"),
            ("IsCrmTemplate", "is_crm_template"),
            ("HasSpCrmBlock", "has_sp_crm_block"),
            ("PersonalFromName", "personal_from_name"),
            ("PersonalFromAddress", "personal_from_address"),
            ("PersonalReplyTo", "personal_reply_to"),
            )),
        ("MessageBodies", (
            ("HTMLBody", "html_body"),
            ("AOLBody", "aol_body"),
            ("TextBody", "text_body"),
            )),
        ("ClickThroughs", (
            ("ClickThrough", "click_throughs"),
            )),
        ("ForwardToFriend", (
            ("ForwardType", "0"),  # This is a required but static value in the API method.
            )),
        ))
    def save_mailing(self, mailing_name, subject, list_id, from_name,
            from_address, reply_to, shared, encoding, tracking_level,
            click_throughs, mailing_id=None, folder_path=None,
            click_here_message=None, is_crm_template=None,
            has_sp_crm_block=None, personal_from_name=None,
            personal_from_address=None, personal_reply_to=None, html_body=None,
            aol_body=None, text_body=None):
        pass

    @api_method("CreateContactList", definition=(
        ("DATABASE_ID", "database_id"),
        ("CONTACT_LIST_NAME", "contact_list_name"),
        ("VISIBILITY", "shared"),
        ("PARENT_FOLDER_ID", "parent_folder_id"),
        ("PARENT_FOLDER_PATH", "parent_folder_path"),
        ))
    def create_contact_list(self, database_id, contact_list_name, shared,
            parent_folder_id=None, parent_folder_path=None):
        pass

    @api_method("AddContactToContactList", definition=(
        ("CONTACT_LIST_ID", "contact_list_id"),
        ("CONTACT_ID", "contact_id"),
        ("COLUMN", "columns"),
        ))
    def add_contact_to_contact_list(self, contact_list_id, contact_id=None,
            columns=None):
        pass


class SilverpopResponseException(Exception):
    pass


class ApiResponse(object):
    def __init__(self, response):
        logger.debug("Response: %s" % response.text)
        self.response_raw = response.text
        self.response = ElementTree.fromstring(self.response_raw)

        success_el = self.response.find(".//SUCCESS")
        if success_el.text.lower() == "false":
            fault_string = self.response.find(".//Fault/FaultString").text
            raise SilverpopResponseException(fault_string)
