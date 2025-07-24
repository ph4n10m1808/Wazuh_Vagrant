# src/config/__init__.py

from .config import REDIS_CONF, ALERT_QUEUE, OS_CONF, OS_INDEX
import json
import os

def load_fields_to_drop():
    path = os.path.join(os.path.dirname(__file__), "fields_to_drop.json")
    with open(path, "r") as f:
        return json.load(f)
def load_tags_config():
    path = os.path.join(os.path.dirname(__file__), "tags_config.json")
    with open(path, "r") as f:
        return json.load(f)

