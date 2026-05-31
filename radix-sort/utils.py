def parse_input(text):
    text = text.strip()

    if not text:
        return None

    try:
        return list(map(int, text.split()))
    except ValueError:
        return "invalid"
