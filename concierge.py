#!/usr/bin/env python3
import os, time, random, requests
from dotenv import load_dotenv
load_dotenv()

PROVIDERS = [
    {
        "name": "cerebras",
        "key": os.getenv("CEREBRAS_API_KEY",""),
        "url": "https://api.cerebras.ai/v1/chat/completions",
        "model": os.getenv("CEREBRAS_MODEL","gpt-oss-120b"),
        "headers": lambda k: {"Authorization": f"Bearer {k}", "Content-Type": "application/json"},
    },
    {
        "name": "openrouter",
        "key": os.getenv("OPENROUTER_API_KEY",""),
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "model": os.getenv("OPENROUTER_MODEL","nvidia/nemotron-3-super-120b-a12b:free"),
        "headers": lambda k: {"Authorization": f"Bearer {k}", "Content-Type": "application/json"},
    },
    {
        "name": "groq",
        "key": os.getenv("GROQ_API_KEY",""),
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "model": os.getenv("GROQ_MODEL","llama-3.3-70b-versatile"),
        "headers": lambda k: {"Authorization": f"Bearer {k}", "Content-Type": "application/json"},
    },
    {
        "name": "gemini",
        "key": os.getenv("GEMINI_API_KEY",""),
        "url": None,
        "model": os.getenv("GEMINI_MODEL","gemini-2.0-flash"),
        "headers": lambda k: {"Content-Type": "application/json"},
    },
]

def _try_provider(p, prompt, system, msgs):
    if p["name"] == "gemini":
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{p['model']}:generateContent?key={p['key']}"
        payload = {"contents":[{"parts":[{"text":prompt}]}]}
        if system:
            payload["system_instruction"] = {"parts":[{"text":system}]}
        r = requests.post(url, json=payload, timeout=30)
        if r.status_code == 429:
            return None, "rate"
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"], None
    r = requests.post(
        p["url"],
        headers=p["headers"](p["key"]),
        json={"model":p["model"],"messages":msgs,"max_tokens":800},
        timeout=30
    )
    if r.status_code == 429:
        return None, "rate"
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"], None

def call_model(prompt, system=None, chairman=False, tries=3):
    msgs = []
    if system:
        msgs.append({"role":"system","content":system})
    msgs.append({"role":"user","content":prompt})

    delay = 2
    for attempt in range(tries):
        all_rate_limited = True
        for p in PROVIDERS:
            if not p["key"]:
                continue
            try:
                text, status = _try_provider(p, prompt, system, msgs)
                if status == "rate":
                    print(f"  [{p['name']}] rate limited, trying next...")
                    continue
                all_rate_limited = False
                return text, p["name"]
            except Exception as e:
                all_rate_limited = False
                print(f"  [{p['name']}] failed: {e}")
                continue
        # full pass failed -- back off before next sweep
        if attempt < tries - 1:
            wait = delay + random.uniform(0, 1)
            print(f"  [concierge] all providers busy, backing off {wait:.1f}s (pass {attempt+2}/{tries})")
            time.sleep(wait)
            delay *= 2

    raise RuntimeError("All providers failed after retries")

def generate(prompt, system=None, chairman=False):
    """Wrapper to maintain compatibility with expected 'generate' interface."""
    return call_model(prompt, system=system, chairman=chairman)
