import re, html

def clean_text(text: str, max_len: int = 4000) -> str:
    text = html.unescape(text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:max_len]
