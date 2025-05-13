import os, json, logging, openai, asyncio
openai.api_key = os.getenv("OPENAI_API_KEY")

PROMPT_HEADER = (
    "You are an expert AI news editor.\n"
    "Task: 1) Summarize in ≤ 50 words (keep original language); "
    "2) Explain why it matters in ≤ 20 words; "
    "3) Rate impact 1‑5.\n"
    "Return ONLY valid JSON like: "
    '{"summary":"...","why":"...","impact":3}'
)

FAST_MODEL = os.getenv("MODEL_FAST", "gpt-3.5-turbo")
PREMIUM_MODEL = os.getenv("MODEL_PREMIUM", "gpt-4o-mini")

async def call_llm(model: str, content: str, temperature: float=0.2):
    resp = await openai.ChatCompletion.acreate(
        model=model,
        messages=[{"role":"user", "content": PROMPT_HEADER + "\n\n" + content}],
        temperature=temperature,
        timeout=20,
    )
    usage = resp.usage
    cost_rate = 0.00001 if model==FAST_MODEL else 0.00003
    cost = (usage.prompt_tokens + usage.completion_tokens) * cost_rate
    text = resp.choices[0].message.content.strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        logging.warning("Invalid JSON from LLM: %s", text)
        data = {"summary":"", "why":"", "impact":1}
    data["llm_model"] = model
    data["cost_usd"] = round(cost,4)
    return data

async def summarize(item: dict, importance_hint: int=1):
    content = f"Title: {item['title']}\nURL: {item['url']}"
    data = await call_llm(FAST_MODEL, content)
    if max(data.get("impact",1), importance_hint) >=4:
        data = await call_llm(PREMIUM_MODEL, content, temperature=0)
    return data
