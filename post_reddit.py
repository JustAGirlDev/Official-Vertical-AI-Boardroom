#!/usr/bin/env python3
"""
Post Mrs Higgins' gig listings to Reddit r/forhire
No API key needed for reading, OAuth for posting
Simplest path to eyeballs on your services
"""
import json, urllib.request, urllib.parse

# Read routing log
with open('/storage/emulated/0/RootBase/src/saas/higgins/front_desk_routing_log.json') as f:
    gigs = json.load(f)

print(f"Found {len(gigs)} gigs ready to post:\n")
for g in gigs:
    print(f"  [{g['platform']}] {g['package_name']}")
    print(f"  Status: {g['status']}")
    print()

print("Manual posting targets:")
print("  r/forhire -- https://reddit.com/r/forhire")
print("  r/slavelabour -- https://reddit.com/r/slavelabour") 
print("  r/DeveloperJobs -- https://reddit.com/r/DeveloperJobs")
print()
print("Format for r/forhire:")
print("[OFFERING] [Android/AI Dev] [Worldwide/Remote] -- $99+")
print()

# Print first gig formatted for Reddit
g = gigs[0]
lines = g['summary'].split('\n')
title_line = f"[OFFERING] Android Dev Environment Setup - Termux Full Stack $99 [Worldwide/Remote]"
print("TITLE:")
print(title_line)
print()
print("BODY:")
for line in lines:
    if line.strip():
        print(line)
