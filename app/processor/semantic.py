import os, openai, json, math, asyncio

openai.api_key = os.getenv("OPENAI_API_KEY")

EMBED_MODEL = "text-embedding-3-small"

async def embed(text: str) -> list[float]:
    res = await openai.Embedding.acreate(model=EMBED_MODEL, input=text)
    return res["data"][0]["embedding"]

def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x*y for x,y in zip(a,b))
    return dot / ((sum(x*x for x in a)**0.5)*(sum(y*y for y in b)**0.5)+1e-9)

async def is_duplicate(new_emb: list[float], existing_embs: list[list[float]], threshold: float=0.92):
    for e in existing_embs:
        if cosine(new_emb, e) >= threshold:
            return True
    return False
