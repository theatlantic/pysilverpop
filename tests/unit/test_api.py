""" WIP: Testing added methods """
import pytest

from silverpop.api import relational_table_create, relational_table_api_method
from silverpop.utils import RelationalTableEntry


@pytest.fixture
def create_method_fixture():
    return relational_table_create("CreateTable")._build_tree


@pytest.fixture
def upsert_method_fixture():
    return relational_table_api_method(
        "InsertUpdateRelationalTable")._build_tree


@pytest.fixture
def col_values_fixture():
    # quick "blank relational table --
    return RelationalTableEntry().columns


@pytest.fixture  # there is def a better way to do this
def row_values_fixture(sender_email_fixture,
                       recipient1_fixture,
                       recipient2_fixture,
                       recipient3_fixture):
    """ relational table row values to update"""

    rows = []
    recipients = [recipient1_fixture, recipient2_fixture, recipient3_fixture]
    for recipient in recipients:
        entry = RelationalTableEntry()
        # TODO: UNIQUE ROWS
        entry.update_values(**{
            "donor_email": sender_email_fixture,
            "recipient_email": recipient.email,  # will be easier to parametrize
            "is_gift_subscription": "true",
            "stripe_subscription_id": recipient.stripe_subscription_id,
            "stripe_coupon_id": recipient.stripe_coupon_id,
            "recipient_stripe_customer_id": recipient.recipient_stripe_customer_id,  # noqa
            "subscription_redeem_url": "https://test.com"
        })
        rows.append(entry.values)

    return rows


# =============== WIP: Test Added Function Request Bodies  ====================

@pytest.mark.skip(reason="WIP")
def test_setup_relational_table():
    pass


@pytest.mark.skip(reason="WIP")
def test_upsert_relational_table_xml(upsert_method_fixture,
                                     relational_table_id_fixture,
                                     row_values_fixture):

    # TODO: "print table"
    string_tree = upsert_method_fixture(
        **{"table_id": relational_table_id_fixture,
           "rows": row_values_fixture}
    )

    assert string_tree  # WIP


@pytest.mark.skip(reason="WIP")
def test_relational_table_entry():
    entry = RelationalTableEntry()
    values = entry.values
    columns = entry.columns
    assert values
