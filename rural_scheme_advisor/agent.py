"""Agentic RAG pipeline:
 1. Profile extraction  -> understands the user's situation from the chat
 2. Retrieval tool      -> RAG over official scheme documents
 3. Eligibility tool    -> rule-based screening
 4. Answer synthesis    -> personalised, step-by-step, in Tamil or English
"""
import json
import re
from openai import OpenAI
from config import NEXUS_API_KEY, NEXUS_BASE_URL, NEXUS_MODEL, TOP_K
from eligibility import check_eligibility

client = OpenAI(api_key=NEXUS_API_KEY, base_url=NEXUS_BASE_URL)


def _chat(messages, temperature=0.2):
    resp = client.chat.completions.create(
        model=NEXUS_MODEL, messages=messages, temperature=temperature
    )
    return resp.choices[0].message.content.strip()


def extract_profile(question: str, history: list, profile: dict) -> dict:
    """LLM tool: pull user details out of the conversation as JSON."""
    prompt = (
        "Extract user details from the message. Return ONLY JSON with keys: "
        "age(int|null), gender(str|null), occupation(str|null), annual_income(int|null), "
        "owns_land(bool|null), has_pucca_house(bool|null), state(str|null), "
        "has_girl_child_under_10(bool|null), search_query_english(str). "
        "search_query_english = the question rewritten as an English search query.\n\n"
        f"Known profile: {json.dumps(profile)}\nMessage: {question}"
    )
    raw = _chat([{"role": "user", "content": prompt}], temperature=0)
    match = re.search(r"\{.*\}", raw, re.S)
    try:
        data = json.loads(match.group(0)) if match else {}
    except json.JSONDecodeError:
        data = {}
    return data


def answer(question: str, history: list, profile: dict, retriever, lang: str = "auto"):
    # Step 1: understand user
    extracted = extract_profile(question, history, profile)
    query_en = extracted.pop("search_query_english", question)
    for k, v in extracted.items():
        if v is not None:
            profile[k] = v

    # Step 2: RAG retrieval (original + English query)
    hits = retriever.search(question, TOP_K) + retriever.search(query_en, TOP_K)
    seen, context_chunks = set(), []
    for h in sorted(hits, key=lambda x: -x["score"]):
        if h["text"] not in seen:
            seen.add(h["text"])
            context_chunks.append(h)
        if len(context_chunks) >= TOP_K:
            break
    context = "\n\n---\n\n".join(f"[{h['source']}]\n{h['text']}" for h in context_chunks)

    # Step 3: eligibility tool
    elig = check_eligibility(profile)
    elig_text = "\n".join(f"- {n}: {why} ({status})" for n, why, status in elig)

    # Step 4: synthesize
    lang_rule = {
        "Tamil": "Reply in simple, spoken Tamil (Tamil script).",
        "English": "Reply in simple English.",
    }.get(lang, "Reply in the same language the user used (Tamil or English).")

    system = (
        "You are 'Rural Scheme Advisor', a friendly assistant helping rural people "
        "understand Indian government schemes. Use ONLY the provided context for facts. "
        "If the context does not contain the answer, say so and suggest visiting the "
        "nearest CSC / panchayat office. Use short sentences and simple words. "
        "Structure answers as: Scheme name, Benefits, Eligibility, Documents required, "
        "How to apply (numbered steps). If key user details are missing for a "
        "personalised answer, ask ONE short follow-up question at the end. "
        f"{lang_rule}"
    )
    user_msg = (
        f"User profile so far: {json.dumps(profile, ensure_ascii=False)}\n\n"
        f"Eligibility screening:\n{elig_text}\n\n"
        f"Retrieved context:\n{context}\n\n"
        f"Question: {question}"
    )
    msgs = [{"role": "system", "content": system}] + history[-6:] + [
        {"role": "user", "content": user_msg}
    ]
    reply = _chat(msgs, temperature=0.3)
    return reply, profile, context_chunks, elig
