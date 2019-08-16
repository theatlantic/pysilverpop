""" WIP: Testing added methods """
from xml.etree import ElementTree

import pytest

from silverpop.api import relational_table_api_method
from silverpop.utils import RelationalTableEntry


@pytest.fixture
def create_method_fixture():
    return relational_table_api_method("CreateTable")._build_tree

@pytest.fixture
def delete_method_fixture():
    return relational_table_api_method("DeleteRelationalTableData")._build_tree


@pytest.fixture
def upsert_method_fixture():
    return relational_table_api_method(
        "InsertUpdateRelationalTable")._build_tree


@pytest.fixture
def col_values_fixture():
    # quick "blank relational table --
    return RelationalTableEntry().columns


@pytest.fixture  # there is def a better way to do this
def row_values_fixture(sender_fixture,
                       recipient1_fixture,
                       recipient2_fixture,
                       recipient3_fixture):
    """ relational table row values to update"""
    rows = []
    recipients = [recipient1_fixture, recipient2_fixture, recipient3_fixture]
    for recipient in recipients:
        entry = RelationalTableEntry()
        entry.update_values(**{
            "donor_email": sender_fixture.email,
            "recipient_email": recipient.email,
            "is_gift_subscription": "true",
            "stripe_subscription_id": recipient.stripe_subscription_id,
            "stripe_coupon_id": recipient.stripe_coupon_id,
            "recipient_stripe_customer_id": recipient.recipient_stripe_customer_id,  # noqa
            "subscription_redeem_url": "https://test.com"
        })

        rows.append(entry.values)

    return rows

@pytest.fixture
def row_values_expected():
    return """
    <Envelope>
	<Body>
	<InsertUpdateRelationalTable>
	<TABLE_ID>12036175</TABLE_ID>
	<ROWS>
	<ROW>
	<COLUMN name="donor_email">test@test.com</COLUMN>
	<COLUMN name="stripe_coupon_id">uuid123</COLUMN>
	<COLUMN name="recipient_email">test-recipient@gmail.com</COLUMN>
	<COLUMN name="is_gift_subscription">true</COLUMN>
	<COLUMN name="stripe_subscription_id">123445xxx</COLUMN>
	<COLUMN name="recipient_stripe_customer_id">1234gj</COLUMN>
	<COLUMN name="subscription_redeem_url">https://test.com</COLUMN>
	</ROW>
	</ROWS>
	</InsertUpdateRelationalTable>
	</Body>
    </Envelope>
    """

# =============== WIP: Test Added Function Request Bodies  ====================


def test_upsert_relational_table_xml(upsert_method_fixture,
                                     relational_table_id_fixture,
                                     row_values_expected):

    string_tree = upsert_method_fixture(
        **{
            "table_id": relational_table_id_fixture,
            "rows": [
                {
                    "donor_email": "test@test.com",
                    "recipient_email": "test-recipient@gmail.com",
                    "is_gift_subscription": "true",
                    "stripe_subscription_id": "123445xxx",
                    "stripe_coupon_id": "uuid123",
                    "recipient_stripe_customer_id": "1234gj",  # noqa
                    "subscription_redeem_url": "https://test.com"
                }
            ]
        }
    )
    assert string_tree
    valid_xml = ElementTree.fromstring(row_values_expected)
    tttt = string_tree.decode("utf-8")
    vvvv = ElementTree.tostring(valid_xml)
    import pdb; pdb.set_trace()
    assert tttt == vvvv


@pytest.mark.skip(reason="WIP")
def test_relational_table_entry():
    entry = RelationalTableEntry()
    values = entry.values
    columns = entry.columns
    assert values
