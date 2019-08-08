import collections
import os

import pytest

from silverpop import utils


# TODO: use either accounts-api model or RowEntry from utils
GiftUser = collections.namedtuple('GiftUser', ['email',
                                               'stripe_subscription_id',
                                               'stripe_coupon_id',
                                               "recipient_stripe_customer_id"])


@pytest.fixture
def sender_id_fixture():
    return os.environ["TEST_SENDER_ID"]


@pytest.fixture
def sender_email_fixture():
    return os.environ["TEST_SENDER_EMAIL"]


# TMP/WIP -- to be pytest.parametrized
@pytest.fixture
def recipient1_fixture():
    return GiftUser(
        os.environ["TEST_RECIPIENT_EMAIL"],
        "123445xxx",
        "uuid123",
        "1234gj"
    )


@pytest.fixture
def recipient2_fixture():
    """ General Recipient, TMP """
    return GiftUser(
        os.environ["TEST_RECIPIENT2_EMAIL"],
        "xxx123445",
        "123uuid",
        "gj1234"
    )  # TODO: test variety


@pytest.fixture
def recipient3_fixture():
    """ General Recipient, TMP """
    return GiftUser(
        os.environ["TEST_RECIPIENT2_EMAIL"],
        "xxx123445",
        "321uuid",
        "gj1234"
    )  # TODO: test variety


@pytest.fixture(autouse=True)
def relational_table_id_fixture():
    return "12036175"


@pytest.fixture  # WIP: there is def a better way to do this
def row_values_fixture(sender_email_fixture,  # TODO: parametrize
                       recipient1_fixture, recipient2_fixture,
                       recipient3_fixture):
    """ relational table row values to update"""
    rows = []
    recipients = [recipient1_fixture, recipient2_fixture, recipient3_fixture]
    for recipient in recipients:
        # WIP: not great to use a testible entity in a fixture
        entry = utils.RelationalTableEntry()
        # TODO: UNIQUE ROWS
        entry.update_values(**{
            "donor_email": sender_email_fixture,
            # will be easier to parametrize
            "recipient_email": recipient.email,
            "is_gift_subscription": "true",
            "stripe_subscription_id": recipient.stripe_subscription_id,
            "stripe_coupon_id": recipient.stripe_coupon_id,
            "recipient_stripe_customer_id": recipient.recipient_stripe_customer_id,  # noqa
            "subscription_redeem_url": "https://test.com"
        })
        rows.append(entry.values)

    return rows
