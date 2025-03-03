from datetime import datetime, timezone

def get_utc_timestamp():
    """Return the current local time in ISO format with timezone offset."""
    
    return  datetime.now(timezone.utc)

def get_utc_offset():
    """Return the current UTC offset in minutes."""
    # Get local timezone
    local_time = datetime.now().astimezone()
    offset = local_time.utcoffset().total_seconds() / 60
    return offset

print(get_utc_offset())

