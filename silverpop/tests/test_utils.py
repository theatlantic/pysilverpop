import unittest

from silverpop.utils import replace_in_nested_mapping, map_to_xml


class TestReplaceNestedMapping(unittest.TestCase):

    def test_basic_mapping(self):
        mapping = (("ABC", "abc"),)
        expected_mapping = (("ABC", "success"),)

        updated_mapping = replace_in_nested_mapping(mapping, {"abc": "success"})

        self.assertEqual(expected_mapping, updated_mapping)

    def test_preserve_order(self):
        mapping = (("ABC", "abc"), ("DEF", "def"))
        expected_mapping = (("ABC", "success"), ("DEF", "def"))

        updated_mapping = replace_in_nested_mapping(mapping, {"abc": "success"})

        self.assertEqual(expected_mapping, updated_mapping)

    def test_nested_mapping(self):
        mapping = (("ABC", (("DEF", "ghi"),)),)
        expected_mapping = (("ABC", (("DEF", "success"),)),)

        updated_mapping = replace_in_nested_mapping(mapping, {"ghi": "success"})

        self.assertEqual(expected_mapping, updated_mapping)


class TestMapToXml(unittest.TestCase):
    def test_one_tag(self):
        mapping = (("ABC", "abc"),)
        expected_xml = "<Envelope><Body><ABC>abc</ABC></Body></Envelope>"

        xml = map_to_xml(mapping)
        self.assertEqual(expected_xml, xml)

    def test_nested_tags(self):
        mapping = (("ABC", (("DEF", "def"),)),)
        expected_xml = "<Envelope><Body><ABC><DEF>def</DEF></ABC></Body></Envelope>"

        xml = map_to_xml(mapping)
        self.assertEqual(expected_xml, xml)
