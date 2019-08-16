import pytest

from silverpop import api, utils
from tests import mock_env  # TODO: mock_env


@pytest.fixture
def silverpop_client_fixture():
    return api.Silverpop(**mock_env.SILVERPOP['KEYS'])


@pytest.fixture
def silverpop_db_id():
    return mock_env.SILVERPOP_DATABASE_ID


@pytest.fixture  # WIP: there is def a better way to do this
def row_values_fixture(sender_email_fixture,  # TODO: parametrize
                       recipient1_fixture,
                       recipient2_fixture):
    """ relational table row values to update"""
    rows = []
    recipients = [recipient1_fixture, recipient2_fixture]
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
