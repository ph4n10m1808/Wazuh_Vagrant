from config import load_tags_config

tags_config = load_tags_config()

def enrich_tags(alert: dict) -> dict:
    host_criticality = "unknown"
    user_role = "unknown"

    # Host criticality
    agent = alert.get("agent.name", "").lower()
    for level, keywords in tags_config.get("host_criticality", {}).items():
        if any(k in agent for k in keywords):
            host_criticality = level
            break

    # User role
    # user = (
    #     alert.get("data.user") or
    #     alert.get("data.srcuser") or
    #     alert.get("user") or ""
    # ).lower()

    # for role, keywords in tags_config.get("user_role", {}).items():
    #     if any(k in user for k in keywords):
    #         user_role = role
    #         break

    # Gán thành các trường riêng
    alert["host_criticality"] = host_criticality
    # alert["user_role"] = user_role

    return alert
