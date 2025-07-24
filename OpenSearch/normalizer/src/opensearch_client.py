# src/opensearch_client.py

import urllib3
from opensearchpy import OpenSearch
from config import OS_CONF

# Disable SSL warnings (use with caution in production)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def connect_opensearch():
    return OpenSearch(**OS_CONF)
