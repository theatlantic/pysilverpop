import inspect
import logging
import six
from xml.etree import ElementTree

from requests_oauthlib import OAuth2Session

from .utils import replace_in_nested_mapping, map_to_xml, get_envelope

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

        if hasattr(inspect, 'getfullargspec'):
            argspec = inspect.getfullargspec(func)
        else:
            argspec = inspect.getargspec(func)

        def wrapper(self, *args, **kwargs):
            # Name the args via zip and then put them in the kwargs.
            values = zip(argspec.args[1:], args)
            kwargs.update(values)
            tree = outer_self._build_tree(**kwargs)
            return self._call(tree)

        # Preserve the argument signature of the wrapped function.
        # fullargspec preserves the defaults while argspec does not.
        if hasattr(inspect, 'signature'):
            func_signature = inspect.signature(func)
            full_argspec = str(func_signature)
            params = func_signature.parameters
            non_default_params = [
                params[p].replace(default=inspect.Parameter.empty)
                for p in argspec.args]
            non_default_argspec = "(%s)" % ', '.join([str(p) for p in non_default_params])
        else:
            full_argspec = inspect.formatargspec(*argspec)
            non_default_argspec = inspect.formatargspec(argspec.args)

        new_func = ("def %s%s:\n"
                    "    return wrapper%s" % (func.__name__, full_argspec, non_default_argspec))
        exec_scope = {"wrapper": wrapper, }

        # Execute the signature-preserving wrapper function in a dict-based
        # closure and return it.
        six.exec_(new_func, exec_scope)
        new_func = exec_scope[func.__name__]
        new_func.__doc__ = self.build_doc(func)
        return new_func

    def build_doc(self, func=None):
        return ":API Method: ``%s``\n%s\n" % (self.cmd_name, func.__doc__ or "")

    def _build_tree(self, **kwargs):
        definition = replace_in_nested_mapping(self.definition, kwargs)
        return map_to_xml(definition, command=self.cmd_name)


class relational_table_api_method(api_method):
    """
    The InsertUpdateRelationalTable API method needs attributes in it. So
    instead of::

        <COLUMN>
            <NAME></NAME>
            <VALUE></VALUE>
        </COLUMN>

    It's::

        <COLUMN name=""></COLUMN>

    So we need to give it its own serializer.
    """
    def _build_tree(self, **kwargs):
        envelope, root = get_envelope(self.cmd_name)

        table_id = kwargs.pop("table_id")
        rows = kwargs.pop("rows")

        # Add the TABLE_ID tag
        table_id_tag = ElementTree.Element("TABLE_ID")
        table_id_tag.text = table_id
        root.append(table_id_tag)

        # Add the ROWS tag
        rows_tag = ElementTree.Element("ROWS")
        root.append(rows_tag)

        # Iterate over the rows.
        for row in rows:
            row_tag = ElementTree.Element("ROW")
            rows_tag.append(row_tag)
            for key, value in six.iteritems(row):
                column_tag = ElementTree.Element("COLUMN")
                column_tag.attrib['name'] = key
                column_tag.text = value
                row_tag.append(column_tag)

        return ElementTree.tostring(envelope)


class Silverpop(object):
    """
    :param str client_id: Silverpop OAuth client id.
    :param str client_secret: Silverpop OAuth client secret.
    :param str refresh_token: Silverpop OAuth refersh token.
    :param int server_number: Silverpop auth server number. Interpolated into API subdomain.

    The Silverpop object is a wrapper around Silverpop's XML API. Roughly, the
    wrapper's methods are underscore-spaced versions of the XML's camel-cased
    methods (Ex: ``SendMailing`` becomes the Python method ``send_mailing``).

    Arguments passed to the methods are lowercase and underscore-spaced
    versions of their relative XML arguments with a few common exceptions:

    * ``<Visibility>`` always becomes ``shared``.
    * For nested lists, the plural is always used: A ``<SUPPRESSION_LIST>``
      inside ``<SUPPRESSION_LISTS>`` will be set with ``suppression_lists``.
    * Each ``<Column>`` will always be set with a key/value in a ``dict`` named
      ``columns``

    .. seealso::

        Every public method on this class uses the :class:`silverpop.api.api_method`
        decorator.

    .. note::

        Silverpop uses a modified OAuth 2 system that uses a refresh token to
        retrieve an access token, even for the first grant. Generally, OAuth 2
        grants an access token and a refresh token initially.
    """
    oauth_endpoint = "https://api-campaign-us-%s.goacoustic.com/oauth/token"
    api_endpoint = "https://api-campaign-us-%s.goacoustic.com/XMLAPI"

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
        self.session = OAuth2Session(
            auto_refresh_kwargs=refresh_kwargs,
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
    def schedule_mailing(
            self, template_id, list_id, mailing_name, send_html=False,
            send_text=False, subject=None, from_name=None, from_address=None,
            reply_to=None, shared=True, scheduled=None, inbox_monitor=None,
            send_time_optimization=None, wa_mailinglevel_code=None,
            suppression_lists=None, parent_folder_path=None,
            create_parent_folder=None, custom_opt_out=None,
            substitutions=None):
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
    def add_recipient(
            self, list_id, created_from, send_autoreply=False,
            update_if_found=False, allow_html=False, visitor_key=None,
            contact_lists=None, honor_optout_status=False, sync_fields=None,
            columns=None):
        pass

    @api_method("RemoveRecipient", definition=(
        ("LIST_ID", "list_id"),
        ("EMAIL", "email"),
        ("COLUMN", "columns"),
    ))
    def remove_recipient(
            self, list_id, email, columns=None):
        pass

    @api_method("OptOutRecipient", definition=(
        ("LIST_ID", "list_id"),
        ("EMAIL", "email"),
        ("MAILING_ID", "mailing_id"),
        ("RECIPIENT_ID", "recipient_id"),
        ("JOB_ID", "job_id"),
    ))
    def opt_out_recipient(
            self, list_id, email=None, mailing_id=None, recipient_id=None,
            job_id=None):
        pass

    @api_method("UpdateRecipient", definition=(
        ("LIST_ID", "list_id"),
        ("OLD_EMAIL", "old_email"),
        ("RECIPIENT_ID", "recipient_id"),
        ("ENCODED_RECIPIENT_ID", "encoded_recipient_id"),
        ("SEND_AUTOREPLY", "send_autoreply"),
        ("ALLOW_HTML", "allow_html"),
        ("VISITOR_KEY", "visitor_key"),
        ("SYNC_FIELDS", "sync_fields"),
        ("COLUMN", "columns"),
        ("SNOOZE_SETTINGS", (
            ("SNOOZED", "snoozed"),
            ("RESUME_SEND_DATE", "resume_send_date"),
            ("DAYS_TO_SNOOZE", "days_to_snooze"),
        ))
    ))
    def update_recipient(
            self, list_id, old_email=None, recipient_id=None,
            encoded_recipient_id=None, send_autoreply=None, allow_html=None,
            visitor_key=None, sync_fields=None, columns=None, snoozed=None,
            resume_send_date=None, days_to_snooze=None,
    ):
        pass

    @api_method("DoubleOptInRecipient", definition=(
        ("LIST_ID", "list_id"),
        ("SEND_AUTOREPLY", "send_autoreply"),
        ("AUTO_HTML", "auto_html"),
        ("COLUMN", "columns")
    ))
    def double_opt_in_recipient(
            self, list_id, send_autoreply=None, auto_html=None, columns=None):
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
    def save_mailing(
            self, mailing_name, subject, list_id, from_name, from_address,
            reply_to, shared, encoding, tracking_level, click_throughs=[],
            mailing_id=None, folder_path=None, click_here_message=None,
            is_crm_template=None, has_sp_crm_block=None,
            personal_from_name=None, personal_from_address=None,
            personal_reply_to=None, html_body=None, aol_body=None,
            text_body=None):
        pass

    @api_method("GetListMetaData", definition=(
        ("LIST_ID", "list_id"),
    ))
    def get_list_meta_data(self, list_id):
        pass

    @api_method("CreateContactList", definition=(
        ("DATABASE_ID", "database_id"),
        ("CONTACT_LIST_NAME", "contact_list_name"),
        ("VISIBILITY", "shared"),
        ("PARENT_FOLDER_ID", "parent_folder_id"),
        ("PARENT_FOLDER_PATH", "parent_folder_path"),
    ))
    def create_contact_list(
            self, database_id, contact_list_name, shared,
            parent_folder_id=None, parent_folder_path=None):
        pass

    @api_method("AddContactToContactList", definition=(
        ("CONTACT_LIST_ID", "contact_list_id"),
        ("CONTACT_ID", "contact_id"),
        ("COLUMN", "columns"),
    ))
    def add_contact_to_contact_list(
            self, contact_list_id, contact_id=None, columns=None):
        pass

    @api_method("SelectRecipientData", definition=(
        ("LIST_ID", "list_id"),
        ("EMAIL", "email"),
        ("RECIPIENT_ID", "recipient_id"),
        ("ENCODED_RECIPIENT_ID", "encoded_recipient_id"),
        ("VISITOR_KEY", "visitor_key"),
        ("RETURN_CONTACT_LISTS", "return_contact_lists"),
        ("COLUMN", "columns"),
    ))
    def select_recipient_data(
            self, list_id, email=None, recipient_id=None,
            encoded_recipient_id=None, visitor_key=None,
            return_contact_lists=False, columns=None):
        pass

    @api_method("GetReportIdByDate", definition=(
        ("MAILING_ID", "mailing_id"),
        ("DATE_START", "date_start"),
        ("DATE_END", "date_end"),))
    def get_report_id_by_date(self, mailing_id, date_start, date_end):
        return

    @api_method("GetSentMailingsForOrg", definition=(
        ("DATE_START", "date_start"),
        ("DATE_END", "date_end"),
        ("PRIVATE", "private"),
        ("SHARED", "shared"),
        ("SCHEDULED", "scheduled"),
        ("SENT", "sent"),
        ("SENDING", "sending"),
        ("OPTIN_CONFIRMATION", "optin_confirmation"),
        ("PROFILE_CONFIRMATION", "profile_confirmation"),
        ("AUTOMATED", "automated"),
        ("CAMPAIGN_ACTIVE", "campaign_active"),
        ("CAMPAIGN_COMPLETED", "campaign_completed"),
        ("CAMPAIGN_CANCELLED", "campaign_cancelled"),
        ("CAMPAIGN_SCRAPE_TEMPLATE", "campaign_scrape_template"),
        ("INCLUDE_TAGS", "include_tags"),
        ("EXCLUDE_ZERO_SENT", "exclude_zero_sent"),
        ("MAILING_COUNT_ONLY", "mailing_count_only"),
        ("EXCLUDE_TEST_MAILINGS", "exclude_test_mailings"),
    ))
    def get_sent_mailings_for_org(
            self, date_start, date_end, private=None, shared=None,
            scheduled=None, sent=None, sending=None, optin_confirmation=None,
            profile_confirmation=None, automated=None, campaign_active=None,
            campaign_completed=None, campaign_cancelled=None,
            campaign_scrape_template=None, include_tags=None,
            exclude_zero_sent=None, mailing_count_only=None,
            exclude_test_mailings=None):
        pass

    @api_method("GetSentMailingsForList", definition=(
        ("LIST_ID", "list_id"),
        ("DATE_START", "date_start"),
        ("DATE_END", "date_end"),
        ("INCLUDE_CHILDREN", "include_children"),
        ("PRIVATE", "private"),
        ("SHARED", "shared"),
        ("SCHEDULED", "scheduled"),
        ("SENT", "sent"),
        ("SENDING", "sending"),
        ("OPTIN_CONFIRMATION", "optin_confirmation"),
        ("PROFILE_CONFIRMATION", "profile_confirmation"),
        ("AUTOMATED", "automated"),
        ("CAMPAIGN_ACTIVE", "campaign_active"),
        ("CAMPAIGN_COMPLETED", "campaign_completed"),
        ("CAMPAIGN_CANCELLED", "campaign_cancelled"),
        ("CAMPAIGN_SCRAPE_TEMPLATE", "campaign_scrape_template"),
        ("INCLUDE_TAGS", "include_tags"),
        ("EXCLUDE_ZERO_SENT", "exclude_zero_sent"),
        ("MAILING_COUNT_ONLY", "mailing_count_only"),
        ("EXCLUDE_TEST_MAILINGS", "exclude_test_mailings"),
    ))
    def get_sent_mailings_for_list(
            self, list_id, date_start, date_end, include_children=None,
            private=None, shared=None, scheduled=None, sent=None, sending=None,
            optin_confirmation=None, profile_confirmation=None, automated=None,
            campaign_active=None, campaign_completed=None,
            campaign_cancelled=None, campaign_scrape_template=None,
            include_tags=None, exclude_zero_sent=None, mailing_count_only=None,
            exclude_test_mailings=None):
        pass

    @api_method("GetAggregateTrackingForMailing", definition=(
        ("MAILING_ID", "mailing_id"),
        ("REPORT_ID", "report_id"),
        ("TOP_DOMAIN", "top_domain"),
        ("INBOX_MONITORING", "inbox_monitoring"),
        ("PER_CLICK", "per_click"),
    ))
    def get_aggregate_tracking_for_mailing(
            self, mailing_id, report_id, top_domain=None,
            inbox_monitoring=None, per_click=None):
        pass

    @api_method("GetLists", definition=(
        ("VISIBILITY", "visibility"),
        ("LIST_TYPE", "list_type"),
        ("FOLDER_ID", "folder_id"),
        ("INCLUDE_ALL_LISTS", "include_all_lists"),
        ("INCLUDE_TAGS", "include_tags"),
    ))
    def get_lists(
            self, visibility, list_type, folder_id, include_all_lists=None,
            include_tags=None):
        pass

    @relational_table_api_method("InsertUpdateRelationalTable")
    def insert_update_relational_table(self, table_id, rows):
        pass


class SilverpopResponseException(Exception):
    pass


class ApiResponse(object):
    def __init__(self, response):
        logger.debug("Response: %s" % response.text)
        self.response_raw = response.text
        self.response = ElementTree.fromstring(self.response_raw.encode('utf-8'))

        # Very rudimentary mapping of response tags and values into the
        # instance dict. This will probably cause some problems down the line
        # but I'm not sure what they are yet.
        results = self.response.find(".//RESULT")
        if results is not None:
            for value in results:
                if value.tag == "COLUMNS":
                    self.__dict__['COLUMNS'] = {}
                    for column in value:
                        name = column.find("NAME")
                        value = column.find("VALUE")
                        self.__dict__['COLUMNS'][name.text] = value.text
                elif value.tag not in self.__dict__:
                    self.__dict__[value.tag] = self._process_node(value)
                else:
                    if type(self.__dict__[value.tag]) != list:
                        self.__dict__[value.tag] = [self.__dict__[value.tag]]

                    self.__dict__[value.tag] += [self._process_node(value)]

            # If the request was not successful, try to raise a descriptive
            # error.
            if getattr(self, "SUCCESS", "false").lower() == "false":
                fault_string = self.response.find(".//Fault/FaultString").text
                raise SilverpopResponseException(fault_string)

    def _process_node(self, element):
        if element.text and element.text.rstrip():
            return element.text

        value_dict = {}
        for value in element:
            if value.tag in value_dict:
                if type(value_dict[value.tag]) != list:
                    value_dict[value.tag] = [value_dict[value.tag]]
                value_dict[value.tag] += [value.text]
            else:
                value_dict[value.tag] = value.text

        return value_dict
