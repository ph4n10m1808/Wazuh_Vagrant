from config import load_tags_config

tags_config = load_tags_config()

def enrich_tags(alert: dict) -> dict:
    host_criticality = "unknown"
    # Host criticality
    agent = alert.get("agent.name", "").lower()
    for level, keywords in tags_config.get("host_criticality", {}).items():
        if any(k in agent for k in keywords):
            host_criticality = level
            break

    # Gán thành các trường riêng
    alert["host_criticality"] = host_criticality
    return alert
