# src/python/normalizer.py

import uuid
import flatdict
import json
from config import load_fields_to_drop

FIELDS_TO_DROP = load_fields_to_drop()

def normalize_alert(alert_data: dict) -> dict:
    flattened = dict(flatdict.FlatDict(alert_data, delimiter="."))

    for field in FIELDS_TO_DROP:
        flattened.pop(field, None)

    flattened["uuid"] = str(uuid.uuid4())
    flattened["timestamp"] = alert_data.get("timestamp", "now")

    level = flattened.get("rule.level", 0)
    try:
        level = int(level)
    except ValueError:
        level = 0

    if level >= 12:
        severity = "critical"
    elif level >= 7:
        severity = "high"
    elif level >= 4:
        severity = "medium"
    else:
        severity = "low"

    flattened["severity"] = severity
    return flattened

def process_alert(alert_json):
    try:
        alert_data = json.loads(alert_json)
    except json.JSONDecodeError:
        return None
    return normalize_alert(alert_data)
