import pdb

import pytest

from silverpop import utils


@pytest.mark.skip(reason="SKIP ME")
def test_select_data(silverpop_client_fixture,
                     silverpop_db_id,
                     sender_email_fixture,
                     recipient1_fixture):

    """
    Example:
        <Envelope>
          <Body>
            <SelectRecipientData>
            <LIST_ID>45654</LIST_ID>
            <EMAIL>someone@adomain.com</EMAIL>
            <COLUMN>
              <NAME>Customer Id</NAME>
              <VALUE>123-45-6789</VALUE>
            </COLUMN>
          </SelectRecipientData>
         </Body>
        </Envelope>
    """

    api_response = silverpop_client_fixture.\
        select_recipient_data(silverpop_db_id,
                              sender_email_fixture
        )

    pdb.set_trace()
    # TODO: client.select_recipient data or if its return  does not include
    # relational data, parse client.ExportTable
    assert api_response.SUCCESS.upper() == "TRUE"


def test_select_data_relational(silverpop_client_fixture,
                                relational_table_id_fixture,
                                sender_email_fixture,
                                row_values_fixture,
                                recipient1_fixture):

    """
    Won't work
    """

    api_response = silverpop_client_fixture.\
        insert_update_relational_table(relational_table_id_fixture,
                                       row_values_fixture)

    api_response = silverpop_client_fixture.\
        select_recipient_data(relational_table_id_fixture,
                              sender_email_fixture,
                              columns={
                                  "donor_email": sender_email_fixture,
                                  "stripe_coupon_id": recipient1_fixture.stripe_coupon_id,
                                  "recipient_email": recipient1_fixture.email
                              }
        )

    pdb.set_trace()
    # TODO: client.select_recipient data or if its return  does not include
    # relational data, parse client.ExportTable
    assert api_response.SUCCESS.upper() == "TRUE"
