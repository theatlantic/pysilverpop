import collections
import os

import pytest


GiftUser = collections.namedtuple('GiftUser', ['email',
                                               'stripe_subscription_id',
                                               'stripe_coupon_id',
                                               "recipient_stripe_customer_id"])


@pytest.fixture
def sender_id_fixture():
    return os.environ["TEST_SENDER_ID"]


@pytest.fixture
def sender_fixture():
    return GiftUser(
        os.environ["TEST_SENDER_EMAIL"],
        "123445xxx-sender",
        "uuid001",
        "abc1234"
    )


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
    return GiftUser(
        os.environ["TEST_RECIPIENT2_EMAIL"],
        "xxx123445",
        "123uuid",
        "gj1234"
    )


@pytest.fixture
def recipient3_fixture():
    # same recipient, same email; different coupon (gift)
    return GiftUser(
        os.environ["TEST_RECIPIENT2_EMAIL"],
        "xxx123445",
        "321uuid",
        "gj1234"
    )


@pytest.fixture(autouse=True)
def relational_table_id_fixture():
    return "12036175"
