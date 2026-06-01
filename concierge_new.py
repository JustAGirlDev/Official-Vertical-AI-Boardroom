#!/usr/bin/env python3
import os, time, requests
from dotenv import load_dotenv
load_dotenv()

PROVIDERS = [
    {
        "name": "cerebras",
        "key": os.getenv("CEREBRAS_API_KEY",""),
        "url": "https://api.cerebras.ai/v1/chat/completions",
        "model": "gpt-oss-120b",
        "headers": lambda k: {"Authorization": f"Bearer {k}", "Content-Type": "application/json"},
    },
    {
        "name": "openrouter",
        "key": os.getenv("OPENROUTER_API_KEY",""),
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "model": "nvidia/nemotron-3-super-120b-a12b:free",
        "headers": lambda k: {"Authorization": f"Bearer {k}", "Content-Type": "application/json"},
    },
    {
        "name": "groq_disabled",
        "key": os.getenv("GROQ_API_KEY",""),
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "model": "llama-3.3-70b-versatile",
        "headers": lambda k: {"Authorization": f"Bearer {k}", "Content-Type": "application/json"},
    },
    {
        "name": "gemini",
        "key": os.getenv("GEMINI_API_KEY",""),
        "url": None,
        "model": "gemini-2.0-flash",
        "headers": lambda k: {"Content-Type": "application/json"},
    },
]

def call_model(prompt, system=None, chairman=False):
    msgs = []
    if system:
        msgs.append({"role":"system","content":system})
    msgs.append({"role":"user","content":prompt})

    for p in PROVIDERS:
        if not p["key"]:
            continue
        try:
            if p["name"] == "gemini":
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{p['model']}:generateContent?key={p['key']}"
                payload = {"contents":[{"parts":[{"text":prompt}]}]}
                if system:
                    payload["system_instruction"] = {"parts":[{"text":system}]}
                r = requests.post(url, json=payload, timeout=30)
                r.raise_for_status()
                return r.json()["candidates"][0]["content"]["parts"][0]["text"], p["name"]
            else:
                r = requests.post(
                    p["url"],
                    headers=p["headers"](p["key"]),
                    json={"model":p["model"],"messages":msgs,"max_tokens":800},
                    timeout=30
                )
                if r.status_code == 429:
                    print(f"  [{p['name']}] rate limited, trying next...")
                    continue
                r.raise_for_status()
                return r.json()["choices"][0]["message"]["content"], p["name"]
        except Exception as e:
            print(f"  [{p['name']}] failed: {e}")
            continue

    raise RuntimeError("All providers failed")
