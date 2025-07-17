# src/python/opensearch_client.py

from opensearchpy import OpenSearch
from config import OS_CONF

def connect_opensearch():
    return OpenSearch(**OS_CONF)
