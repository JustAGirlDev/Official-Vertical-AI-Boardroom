#!/usr/bin/env python3
"""
VERTICAL AI -- Boardroom Engine
Five agents argue. Chairman synthesizes via Gemini.
No simulated output. No placeholders.
"""

import json
from router import call_model, ModelTier

AGENTS = {
    "CFO": {
        "persona": "You are the CFO. Capital efficiency is everything. Attack every idea on unit economics, burn rate, ROI timeline, and cash position. Brutally honest. You will kill a good idea if the numbers dont work.",
        "focus": "financial viability, cost structure, revenue model, margins"
    },
    "CMO": {
        "persona": "You are the CMO. You live in market positioning, brand narrative, and customer acquisition. Challenge assumptions about who the customer actually is and whether go-to-market can scale. Optimistic but demand evidence.",
        "focus": "market fit, positioning, acquisition cost, brand, customer psychology"
    },
    "CRO": {
        "persona": "You are the Chief Risk Officer. Find every way this fails — legal, regulatory, reputational, operational, competitive. Not a pessimist, a stress tester. If it survives your analysis it is real.",
        "focus": "risk vectors, failure modes, legal exposure, competitive threats, operational fragility"
    },
    "MARKET_ANALYST": {
        "persona": "You are the Market Analyst. Real data on market size, competitive landscape, timing, macro trends. Contextualize every claim against what is actually happening right now. No speculation — extrapolate from evidence.",
        "focus": "market size, timing, competition, macro trends, comparable exits"
    },
    "DEVIL": {
        "persona": "You are the Devils Advocate. Destroy the strongest argument made so far and present the exact opposite as compellingly as possible. Not contrarian for sport — pressure testing every assumption the room has accepted.",
        "focus": "challenging consensus, exposing assumptions, flipping the strongest argument"
    }
}


def run_boardroom(context: dict, rounds: int = 2) -> dict:
    input_summary = json.dumps(context, indent=2)
    debate_log = []

    print(f"\n{'='*60}")
    print("  VERTICAL AI -- BOARDROOM IN SESSION")
    print(f"{'='*60}")
    print(f"  Target: {context.get('label', 'Unknown')}")
    print(f"  Type:   {context.get('type', 'Unknown')}")
    print(f"{'='*60}\n")

    for round_num in range(1, rounds + 1):
        print(f"-- ROUND {round_num} --")

        for agent_name, agent in AGENTS.items():
            prior_args = "\n\n".join([
                f"[{e['agent']}]: {e['argument']}"
                for e in debate_log
            ]) if debate_log else "You are the first to speak."

            prompt = f"""
BOARDROOM INPUT:
{input_summary}

PRIOR ARGUMENTS:
{prior_args}

YOUR TURN. Be specific. Reference actual input data.
Do not summarize others — respond to them or build on them.
Max 200 words. No hedging. No filler.
"""
            print(f"  [{agent_name}] ...", end="", flush=True)
            try:
                response, provider = call_model(
                    prompt,
                    system=f"{agent['persona']}\nFocus: {agent['focus']}",
                    tier=ModelTier.BOARDROOM
                )
                print(f" ({provider})")
                print(f"  {response.strip()}\n")
                debate_log.append({
                    "round": round_num,
                    "agent": agent_name,
                    "argument": response.strip(),
                    "provider": provider
                })
            except RuntimeError as e:
                print(f"\n  FAILED: {e}")
                debate_log.append({
                    "round": round_num,
                    "agent": agent_name,
                    "argument": f"FAILED: {e}",
                    "provider": "none"
                })

    # CHAIRMAN -- Gemini reserved call
    print("\n-- CHAIRMAN SYNTHESIS (Gemini) --")
    print("  Chairman deliberating...", end="", flush=True)

    full_debate = "\n\n".join([
        f"[{e['agent']} R{e['round']}]: {e['argument']}"
        for e in debate_log
        if not e['argument'].startswith("FAILED")
    ])

    chairman_prompt = f"""
ORIGINAL INPUT:
{input_summary}

FULL BOARDROOM DEBATE:
{full_debate}

You are the Chairman. The board has spoken. Now you decide.
Respond in strict JSON only:
{{
  "consensus": "what the room agreed on",
  "primary_risk": "single biggest risk",
  "primary_opportunity": "single biggest opportunity",
  "contested": "what could not be resolved",
  "verdict": "go | no-go | conditional",
  "verdict_condition": "if conditional, what must be true first"
}}
Return ONLY the JSON. No preamble. No markdown.
"""
    try:
        raw, provider = call_model(chairman_prompt, tier=ModelTier.FAST, chairman=True)
        print(f" ({provider})")
        clean = raw.strip().replace("```json","").replace("```","").strip()
        synthesis = json.loads(clean)
    except Exception as e:
        print(f"\n  Chairman failed: {e}")
        synthesis = {"error": str(e)}

    print(f"\n  VERDICT: {synthesis.get('verdict','unknown').upper()}")

    return {"debate": debate_log, "synthesis": synthesis}
