def parse_input(text):
    text = text.strip()

    if not text:
        return None

    try:
        nums = list(map(int, text.split()))
        return nums
    except ValueError:
        return "invalid"
