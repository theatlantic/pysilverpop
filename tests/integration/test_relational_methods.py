import pytest

from silverpop import utils


# HACKY
@pytest.fixture  # WIP: there is def a better way to do this
def row_value_update(sender_email_fixture,  # TODO: parametrize
                     recipient1_fixture,
                     recipient2_fixture,
                     recipient3_fixture):
    """ relational table row values to update"""
    rows = []
    recipients = [recipient1_fixture]  # WIP
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
            "subscription_redeem_url": "https://testing-update-bar.com"
        })
        rows.append(entry.values)

    return rows


# @pytest.mark.skip(reason="SKIP ME")
def test_update_relational(silverpop_client_fixture,
                           relational_table_id_fixture,
                           sender_email_fixture,
                           row_values_fixture,  # TMP, this is gross
                           row_value_update):  # NOT DRY

    """
    When rows are inserted or updated in the relational table, all Column
    values are set based on the values that are passed in the COLUMN elements.
    IBM/customer-engagement/tutorials/insert-update-records-relational-table/
    """
    assert row_values_fixture[0]["donor_email"] == sender_email_fixture

    # TODO: check to see if already present, if so, pass in
    # row_values fixture; just using UI for hack for now, can
    # use silverpopuser? will that give relational?
    api_response = silverpop_client_fixture.\
        insert_update_relational_table(relational_table_id_fixture,
                                       row_value_update)

    # TODO: client.select_recipient data or if its return  does not include
    # relational data, parse client.ExportTable
    assert api_response.SUCCESS.upper() == "TRUE"
