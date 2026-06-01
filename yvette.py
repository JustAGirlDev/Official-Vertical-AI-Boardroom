#!/usr/bin/env python3
"""
YVETTE -- AI Intake Specialist
Named after Yvette Goodrich, Goodrich Plumbing, Alva Oklahoma.
Run: python3 yvette.py
"""
import os, sys, json, urllib.request

KNOWLEDGE = open('/storage/emulated/0/RootBase/Yvette/knowledge/plumbing_core.md').read()

GEMINI_KEY = os.getenv('GEMINI_API_KEY', '')

SYSTEM = f"""You are Yvette, an AI intake specialist for a plumbing and HVAC company.
You have 30 years of trades knowledge. You are warm, direct, and efficient.
You ask the RIGHT diagnostic questions before any truck rolls.
You know what parts to send with the tech before they leave the shop.
You filter price shoppers politely but firmly.
You never guess. You ask one question at a time.

YOUR KNOWLEDGE BASE:
{KNOWLEDGE}

RULES:
- Ask ONE question at a time
- Never recommend a truck roll until you know exactly what's needed
- Always get: location, problem description, house age if relevant
- For HVAC: always ask about filter and blinking lights first
- For plumbing: always ask if there's a cleanout before snaking
- End intake with: parts needed, urgency level, estimated time
"""

history = []

def ask_gemini(prompt):
    if not GEMINI_KEY:
        return "[No API key -- set GEMINI_API_KEY in .env]"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}"
    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM}]},
        "contents": [{"parts": [{"text": m["content"]}], "role": m["role"]} for m in history]
    }
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            result = json.loads(r.read())
        return result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"[Error: {e}]"

def chat(user_input):
    history.append({"role": "user", "content": user_input})
    response = ask_gemini(user_input)
    history.append({"role": "model", "content": response})
    return response

print("\n" + "="*50)
print("  YVETTE -- AI INTAKE SPECIALIST")
print("  Goodrich Plumbing style. All day.")
print("  Type 'quit' to exit, 'reset' to start over")
print("="*50 + "\n")

# Opening
opening = chat("A customer just called. Greet them and ask what's going on.")
print(f"Yvette: {opening}\n")

while True:
    try:
        user = input("Customer: ").strip()
        if not user:
            continue
        if user.lower() == 'quit':
            print("\nYvette: Have a good one. I'll make sure the tech is prepped.")
            break
        if user.lower() == 'reset':
            history.clear()
            print("\n--- NEW CALL ---\n")
            opening = chat("A new customer just called. Greet them and ask what's going on.")
            print(f"Yvette: {opening}\n")
            continue
        response = chat(user)
        print(f"\nYvette: {response}\n")
    except KeyboardInterrupt:
        print("\n\nYvette: Gotta go. Call back anytime.")
        break
