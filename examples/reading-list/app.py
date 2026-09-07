"""A small, deterministic reading-list example. No network or persistence."""
import json
import sys
from urllib.parse import urlsplit

def add_item(items, url):
    value = url.strip()
    if any(char.isspace() or ord(char) < 32 or ord(char) == 127 for char in value):
        raise ValueError("The URL must not contain spaces or control characters.")
    parsed = urlsplit(value)
    parsed.port  # Access validates port syntax and range without a network request.
    if (parsed.scheme not in ("http", "https") or not parsed.hostname
            or parsed.username is not None or parsed.password is not None):
        raise ValueError("Use an HTTP or HTTPS URL with a host and without credentials.")
    if value not in items:
        items.append(value)
    return items

if __name__ == "__main__":
    items = []
    try:
        for value in sys.argv[1:]:
            add_item(items, value)
    except ValueError as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
    print(json.dumps(items))
