from collections import OrderedDict
from xml.etree import ElementTree


def replace_in_nested_mapping(mapping, key, value):
    mapping = OrderedDict(mapping)

    for mapping_key, mapping_value in mapping.items():
        if isinstance(mapping_value, tuple):
            mapping[mapping_key] = replace_in_nested_mapping(mapping_value, key, value)

        if mapping_value == key:
            mapping[mapping_key] = value
            break

    return tuple(mapping.items())


def map_to_xml(mapping, root=None):
    envelope = None

    if root is None:
        envelope = ElementTree.Element("Envelope")
        root = ElementTree.Element("Body")
        envelope.append(root)

    for tag, value in mapping:
        tag = ElementTree.Element(tag)

        if type(value) == tuple:
            value = map_to_xml(value, tag)
        elif not type(value) == bool:
            tag.text = value

        if value:
            root.append(tag)

    if envelope:
        root = envelope
    return ElementTree.tostring(root)

