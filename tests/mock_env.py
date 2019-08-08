from martini.secrets import get_env_var


IBM_POD = get_env_var("IBM_POD")

SILVERPOP_CLIENT_ID = get_env_var("SILVERPOP_CLIENT_ID")
SILVERPOP_CLIENT_SECRET = get_env_var("SILVERPOP_CLIENT_SECRET")
SILVERPOP_REFRESH_TOKEN = get_env_var("SILVERPOP_REFRESH_TOKEN")

SILVERPOP_DATABASE_ID = get_env_var("SILVERPOP_DATABASE_ID")
SILVERPOP_RELATIONAL_TABLE_ID = get_env_var("SILVERPOP_RELATIONAL_TABLE_ID")

# for Silverpop API client instantiation
SILVERPOP = {
    "KEYS": {
        "client_id": SILVERPOP_CLIENT_ID,
        "client_secret": SILVERPOP_CLIENT_SECRET,
        "refresh_token": SILVERPOP_REFRESH_TOKEN,
        "server_number": IBM_POD
    },
    'DATABASE_ID': SILVERPOP_RELATIONAL_TABLE_ID,
    'CIRC_SUPPRESSION_LIST_ID': '7608439',
}
