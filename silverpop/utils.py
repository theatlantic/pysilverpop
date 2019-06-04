from collections import OrderedDict
from xml.etree import ElementTree

import six


def replace_in_nested_mapping(mapping, values):
    """
    Recursively replace "variable names" (strings that have the same value as
    keys in a dict) with their values in a nested 2-tuple mapping.
    """
    definitions = {}

    for (mapping_key, mapping_value) in mapping:
        if isinstance(mapping_value, tuple):
            definitions[mapping_key] = replace_in_nested_mapping(mapping_value, values)
            if len(definitions[mapping_key]) ==  0:
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
                value_list += (((tag.tag), (("NAME", column_name), ("VALUE", column_value))),)

            value = map_to_xml(value_list, root)
            continue

        elif not type(value) == bool:
            # If the value isn't True/False, we can set the node's text value.
            # If the value is True, the tag will still be appended but will be
            # self-closing.
            tag.text = u"%s" % (value)

        if value:
            root.append(tag)

    if envelope is not None:
        root = envelope
    return ElementTree.tostring(root)
