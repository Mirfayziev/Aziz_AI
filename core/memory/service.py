def embed(text: str):
    # Keyin OpenAI embedding bilan almashtiramiz
    return [0.12, 0.88, 0.33]  # Fake vector

def save_vector(db, text, meta=None):
    vec = embed(text)
    obj = MemoryVector(text=text, vector=vec, meta=meta or {})
    db.add(obj)
    db.commit()
    return obj
