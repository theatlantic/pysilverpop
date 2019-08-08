# pylint: disable=missing-docstring
import collections
import six

from xml.etree import ElementTree


class ColumnTypes:
    """
    https://developer.ibm.com/customer-engagement/tutorials/create-relational-table/
    Please note, the 'phone number' type is only available through the UI and
    not the XML API
    """
    text = "TEXT"
    boolean = "YESNO"
    numeric = "NUMERIC"
    date = "DATE"
    time = "TIME"
    country_region = "COUNTRY"
    selection = "SELECTION"
    email = "EMAIL"
    sync_id = "SYNC_ID"
    timestamp = "DATE_TIME"


class RelationalTableEntry:
    def __init__(self):
        self.__keys = [
            ("donor_email", ColumnTypes.email, True),
            ("stripe_coupon_id", ColumnTypes.text, True),
            ("recipient_email", ColumnTypes.email, True),
            ("is_gift_subscription", ColumnTypes.boolean, True),
            ("stripe_subscription_id", ColumnTypes.text, True),
            ("recipient_stripe_customer_id", ColumnTypes.text, True),
            ("subscription_redeem_url", ColumnTypes.text, True)
            # WIP -- Timestamp field format difficult to find in docs
            # ("silverbullet_received_on", ColumnTypes.timestamp, True),
            # ("silverbullet_sent_on", ColumnTypes.timestamp, True),
            # ("modified_on", ColumnTypes.timestamp, True),
            # ("created_on", ColumnTypes.timestamp, True)
        ]
        self.__columns = [
            {"name": key[0], "type": key[1],
                "is_required": "true" if key[2] else "false"}
            for key in self.__keys
        ]

        # Please ignore this hack for now, trying key column
        # combinations
        # TMP -- this is obv not great
        self.__columns[0].update({"key_column": "true"})
        self.__columns[1].update({"key_column": "true"})  # gross
        self.__columns[2].update({"key_column": "true"})  # gross

        self.__values = collections.defaultdict()
        [self.__values.setdefault(key[0]) for key in self.__keys]

    @property
    def columns(self):  # TODO: have pull from api option/verification
        return self.__columns

    @property
    def values(self):  # setter
        return dict(self.__values)

    def update_values(self, **kwargs):
        for key, value in kwargs.items():
            if key not in self.__values:
                raise ValueError("Key %s not in defined columns" % key)
            self.__values[key] = value

        return self.__values


def CDATA(parent, text=None):
    element = ElementTree.SubElement(parent, '![CDATA[')
    element.text = text
    return element


ElementTree._original_serialize_xml = ElementTree._serialize_xml


def _serialize_xml(write, elem, qnames, namespaces, **kwargs):
    if elem.tag == '![CDATA[':
        write("<%s%s]]>" % (elem.tag, elem.text))
        return

    return ElementTree._original_serialize_xml(
        write, elem, qnames, namespaces, short_empty_elements=False)


ElementTree._serialize_xml = ElementTree._serialize['xml'] = _serialize_xml


def replace_in_nested_mapping(mapping, values):
    """
    Recursively replace "variable names" (strings that have the same value as
    keys in a dict) with their values in a nested 2-tuple mapping.
    """
    definitions = {}

    for (mapping_key, mapping_value) in mapping:
        if isinstance(mapping_value, tuple):
            definitions[mapping_key] = replace_in_nested_mapping(
                mapping_value, values)
            if len(definitions[mapping_key]) == 0:
                del definitions[mapping_key]

        if mapping_value in values:
            if values[mapping_value]:
                definitions[mapping_key] = values[mapping_value]

    return tuple(definitions.items())


def get_envelope(command):
    envelope = ElementTree.Element("Envelope")
    root = ElementTree.Element("Body")
    envelope.append(root)

    if command:
        command = ElementTree.Element(command)
        root.append(command)

        root = command

    return (envelope, root)


def map_to_xml(mapping, root=None, command=None):
    """
    Take the nested 2-tuple mapping with values from
    `replace_in_nested_mapping` and turn them into XML that can get passed to
    Silverpop.
    """
    envelope = None

    if root is None:
        envelope, root = get_envelope(command)

    for tag, value in mapping:
        tag = ElementTree.Element(tag)

        if type(value) == tuple:
            # Allow for nesting.
            value = map_to_xml(value, tag)
        elif type(value) == list:
            # This conditional lets us expand lists into multiple elements with
            # the same name:
            #
            #    (("test", (("test_child", [1, 2, 3]),)),)
            #
            # will be serialized as:
            #
            #    <test>
            #         <test_child>1</test_child>
            #         <test_child>2</test_child>
            #         <test_child>3</test_child>
            #    </test>
            value_list = tuple((tag.tag, value) for value in value)
            value = map_to_xml(value_list, root)
            continue
        elif type(value) == dict:
            # This conditional expands dicts into name/value pairs, as required
            # by some Silverpop method:
            #
            #     (("COLUMN", {"a": 1}),)
            #
            # will be serialized as:
            #
            #     <COLUMN>
            #         <NAME>a</NAME>
            #         <VALUE>1</VALUE>
            #     </COLUMN>

            value_list = ()
            for column_name, column_value in six.iteritems(value):
                value_list += (((tag.tag), (("NAME", column_name),
                                            ("VALUE", column_value))),)

            value = map_to_xml(value_list, root)
            continue

        elif not type(value) == bool:
            # If the value isn't True/False, we can set the node's text value.
            # If the value is True, the tag will still be appended but will be
            # self-closing.
            tag.text = u"%s" % (value)

        if value:
            # hack for now
            if tag.tag == "COLUMN":
                dict_root = ElementTree.Element("COLUMNS")
                dict_root.append(tag)
                root.append(dict_root)
            else:
                root.append(tag)

    if envelope is not None:
        root = envelope

    str_tree = ElementTree.tostring(root)
    return str_tree
