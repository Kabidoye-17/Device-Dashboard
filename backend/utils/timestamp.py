from datetime import datetime

def get_timestamp():
    """Return current timestamp in ISO format."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
