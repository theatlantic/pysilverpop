"""
WIP -- unittest to pytest; TODO: use OOTB pytest features (expected, etc)
"""

import pytest

from silverpop.utils import replace_in_nested_mapping, map_to_xml


@pytest.fixture
def basic_mapping_fixture():
    return (("ABC", "abc"),)


# ========================= TestReplaceNestedMapping ==========================
def test_basic_mapping(basic_mapping_fixture):
    updated_mapping = replace_in_nested_mapping(
        basic_mapping_fixture, {"abc": "success"})
    expected_mapping = (("ABC", "success"),)

    assert expected_mapping == updated_mapping


def test_preserve_order():
    """
    CURRENTLY FAILING:
    E       AssertionError: assert (('ABC', 'suc...'DEF', 'def')) == (('ABC', 'success'),)
    E         Left contains one more item: ('DEF', 'def')
    E         Full diff:
    E         - (('ABC', 'success'), ('DEF', 'def'))
    E         + (('ABC', 'success'),)
    """
    mapping = (("ABC", "abc"), ("DEF", "def"))
    expected_mapping = (("ABC", "success"), ("DEF", "def"))

    updated_mapping = replace_in_nested_mapping(mapping, {"abc": "success"})

    assert expected_mapping == updated_mapping


def test_nested_mapping():
    mapping = (("ABC", (("DEF", "ghi"),)),)
    expected_mapping = (("ABC", (("DEF", "success"),)),)

    updated_mapping = replace_in_nested_mapping(mapping, {"ghi": "success"})

    assert expected_mapping == updated_mapping


# ============================= TestMapToXml =================================

def test_one_tag(basic_mapping_fixture):
    expected_xml = b"<Envelope><Body><ABC>abc</ABC></Body></Envelope>"
    xml = map_to_xml(basic_mapping_fixture)
    assert expected_xml == xml


def test_nested_tags():
    mapping = (("ABC", (("DEF", "def"),)),)
    expected_xml = b"<Envelope><Body><ABC><DEF>def</DEF></ABC></Body></Envelope>"

    xml = map_to_xml(mapping)
    assert expected_xml == xml


def test_list():
    mapping = (("ABC", (("DEF", [1, 2]),)),)
    expected_xml = b"<Envelope><Body><ABC><DEF>1</DEF><DEF>2</DEF></ABC></Body></Envelope>"

    xml = map_to_xml(mapping)
    assert expected_xml == xml


def test_dict():
    mapping = (("ABC", (("DEF", {"a": 1}),)),)
    expected_xml = b"<Envelope><Body><ABC><DEF><NAME>a</NAME><VALUE>1</VALUE></DEF></ABC></Body></Envelope>"  # noqa

    xml = map_to_xml(mapping)
    assert expected_xml == xml


def test_key_value_in_list():
    mapping = (("TESTS", (("TEST", [(("a", "b"), ("c", "d")), (("a", "e"), ("c", "f"))]),)),)  # noqa
    expected_xml = (
        b"<Envelope><Body><TESTS>" +
        b"<TEST><a>b</a><c>d</c></TEST>" +
        b"<TEST><a>e</a><c>f</c></TEST>" +
        b"</TESTS></Body></Envelope>")

    xml = map_to_xml(mapping)
    assert expected_xml == xml
