def chunk_text(text: str, max_chars=2000):
    chunks = []
    current = ""

    for line in text.split("\n"):
        if len(current) + len(line) > max_chars:
            chunks.append(current)
            current = ""
        current += line + "\n"

    if current:
        chunks.append(current)

    return chunks
