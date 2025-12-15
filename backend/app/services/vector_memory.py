import openai
import psycopg2
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cur = conn.cursor()

def save_memory(user_id: str, text: str):
    emb = openai.embeddings.create(
        model="text-embedding-3-small",
        input=text
    ).data[0].embedding

    cur.execute(
        "INSERT INTO memory (user_id, content, embedding) VALUES (%s, %s, %s)",
        (user_id, text, emb)
    )
    conn.commit()


def search_memory(user_id: str, text: str):
    emb = openai.embeddings.create(
        model="text-embedding-3-small",
        input=text
    ).data[0].embedding

    cur.execute("""
        SELECT content FROM memory
        ORDER BY embedding <-> %s
        LIMIT 5
    """, (emb,))

    return [row[0] for row in cur.fetchall()]
