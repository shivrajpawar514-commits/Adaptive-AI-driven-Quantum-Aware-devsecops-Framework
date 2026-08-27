from typing import Dict, Any
import datetime


def log_message(session, message: str, level: str = "INFO"):
    """Append a log entry to the execution session.
    """
    timestamp = datetime.datetime.utcnow().isoformat() + "Z"
    session.logs.append(f"{timestamp} {level} {message}")
