# ARCHITECTURE

## Data flow
scout_targets.py / firefly_lite.py / ingest.py   (gather: targets, market intel, codebases)
        |
        v
vertical_ai.py                                    (main CLI, orchestrates everything)
        |
        +-- boardroom.py      5 agents debate (CFO, CMO, CRO, ANALYST, DEVIL) -> Chairman verdict
        +-- simulator.py      fractal market simulation -> strategy tracks
        +-- genetics.py       genetic arena, breeds champion strategy
        +-- (outreach)        JSON payload: email/linkedin/sms variants + objection handlers
        |
        v
vai_output_<session>.json + reports/

## Plumbing
- concierge.py / concierge_new.py  multi-provider client. Order: cerebras -> openrouter -> groq -> gemini.
  Models + keys from .env. 3 backoff sweeps on rate limits. KEEP THESE TWO FILES IDENTICAL.
- router.py / router_v3.py         provider routing. TODO(Mike): models still hardcoded here.
- concierge_v3.py                  TODO(Mike): newest client w/ model registry — which one is canon?
- boardroom_bridge.py              browser <-> CLI bridge for the 3D frontend
- mutation_engine.py               AST-level code mutation (used by Molt experiments)
- yvette.py                        trades-business intake specialist (gemini, hardcoded model — TODO)
- verticals/                       domain context txt files; add new vertical = add file
- web_search.py, cfpb.py, swarm_intel.py, google_business.py  TODO(Mike): document role of each

## Free data sources (no key)
BLS, FRED, World Bank, HackerNews, OpenStreetMap

## Versions
- v2.0-stable (git tag): pinned deps, env-driven concierge models, backoff sweeps
