import re


def sanitize_text(text):

    """
    Basic input sanitization
    """

    text = str(text)

    text = re.sub(
        r"[<>]",
        "",
        text
    )

    return text.strip()