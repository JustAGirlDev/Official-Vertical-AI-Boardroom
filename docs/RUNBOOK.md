# RUNBOOK — Vertical AI Boardroom
Last verified: 2026-06-09 against tag v2.0-stable

## Daily driver commands
    # full boardroom session on an idea
    python vertical_ai.py --text "your idea" --rounds 1 --tracks 2 --iterations 2 --no-neo4j --outreach

    # scout local targets, then board them
    python3 scout_targets.py --location "Wellington KS" --radius 25 --min-score 40
    python vertical_ai.py --file targets/<newest>.txt --rounds 1 --tracks 1 --iterations 1 --no-neo4j --outreach

    # 3D frontend
    python3 boardroom_bridge.py &
    python3 -m http.server 8080 &
    # open http://127.0.0.1:8080/vertical_ai_boardroom_3d.html

## Known failure modes + fixes
- 429 rate limits: concierge now sweeps all providers 3x with backoff (2s/4s/8s).
  If a session still dies, wait 60s and rerun — free tiers reset fast.
- Termux: /tmp does not exist. Anything writing temp files must use ~/.
- Termux: heredocs with nested quotes cause SyntaxErrors. Write file, then run it.
- Heavy pip packages fail to build on ARM64. Prefer stdlib. requirements.txt is the pinned known-good set.
- Relative paths break when run outside the repo dir. Always cd here first.

## Recovery
- Known-good state: git checkout v2.0-stable
- What changed since: git diff v2.0-stable
- Remote: https://github.com/JustAGirlDev/Official-Vertical-AI-Boardroom (auth: JustAGirlDev token, per-repo via credential.useHttpPath)

## Known lies (unfixed)
- scout_targets.py: ratings/review counts are hardcoded defaults (every target shows
  4.0 stars / 100 reviews). OSM does not provide ratings. Do NOT quote these numbers
  in real outreach until the scoring rewrite lands.
