from datetime import datetime

def get_local_time_with_offset():
    """Return the current local time in ISO format with timezone offset."""
    return datetime.now().astimezone().isoformat() 
