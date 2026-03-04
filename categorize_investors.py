#!/usr/bin/env python3
"""Parse vcs-and-angels.csv and categorize each investor into tiers."""

import csv
import json
import re
import os

INPUT_CSV = "/home/user/attachments/vcs-and-angels.csv"
OUTPUT_JSON = "/home/user/agent-f1d448e6/investors_categorized.json"
OUTPUT_JSON_COPY = "/home/user/output/investors_categorized.json"

# ── Tier 1 VC patterns (compiled regexes with word boundaries) ────────────────
# Word-boundary patterns for most Tier 1 names
_TIER1_WB = [
    "andreessen horowitz", "a16z",
    "sequoia",
    "kleiner perkins",
    "lightspeed venture",
    "lightspeed ventures",
    "greylock",
    "general catalyst",
    "union square ventures",
    "bessemer",
    "accel",
    "new enterprise associates",
    "insight partners",
    "benchmark capital",
    "index ventures",
    "tiger global",
    "coatue",
    "excel venture",
    "first round capital",
    "homebrew",
    "y combinator",
    "techstars",
    "500 startups", "500 global",
    "plug and play",
    "social capital",
]
TIER1_PATTERNS = [re.compile(r'\b' + re.escape(kw) + r'\b', re.IGNORECASE) for kw in _TIER1_WB]
# "Founders Fund" must appear at start of name (avoid matching "Female Founders Fund" etc.)
TIER1_PATTERNS.append(re.compile(r'^founders fund\b', re.IGNORECASE))

# ── Accelerator keywords (lowercased) ────────────────────────────────────────
ACCELERATOR_KEYWORDS = [
    "accelerator",
    "incubator",
    "youweb",
]

# ── Angel / Family Office keywords (lowercased) ──────────────────────────────
ANGEL_KEYWORDS = [
    "angel",
    "family",
    "foundation",
    "angels forum",
    "golden seeds",
    "band of angels",
    "arc angel fund",
    "digital irish angels",
    "taiwan global angels",
    "superangel",
    "agi house",
]


def categorize(fund_name: str) -> str:
    name_lower = fund_name.strip().lower()

    # Check Accelerator FIRST (so "Brain Trust Accelerator Fund" isn't caught
    # by Tier 1 "accel" word-boundary match — "accelerator" contains "accel"
    # at a word boundary but should be categorised as Accelerator)
    for kw in ACCELERATOR_KEYWORDS:
        if kw in name_lower:
            return "Accelerator"

    # Check Tier 1 with word-boundary regex
    for pat in TIER1_PATTERNS:
        if pat.search(fund_name):
            return "Tier 1 VC"

    # Check Angel / Family Office
    for kw in ANGEL_KEYWORDS:
        if kw in name_lower:
            return "Angel/Family Office"

    # Default
    return "Tier 2 VC"


def main():
    results = {
        "Angel/Family Office": [],
        "Tier 1 VC": [],
        "Accelerator": [],
        "Tier 2 VC": [],
    }

    with open(INPUT_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            fund_name = (row.get("name") or "").strip()
            contact_name = (row.get("contact") or "").strip()
            email = (row.get("email") or "").strip()
            city = (row.get("city") or "").strip()

            if not fund_name:
                continue

            category = categorize(fund_name)
            missing_email = email == ""

            entry = {
                "fund_name": fund_name,
                "contact_name": contact_name,
                "email": email,
                "city": city,
                "identified_category": category,
                "missing_email": missing_email,
                "potential_aman_overlap": False,
            }

            results[category].append(entry)

    # Write JSON output
    for path in [OUTPUT_JSON, OUTPUT_JSON_COPY]:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as out:
            json.dump(results, out, indent=2, ensure_ascii=False)

    # Summary
    total = sum(len(v) for v in results.values())
    print(f"Total investors processed: {total}")
    for cat, entries in results.items():
        missing = sum(1 for e in entries if e["missing_email"])
        print(f"  {cat}: {len(entries)} entries ({missing} missing email)")
    print(f"\nJSON written to:\n  {OUTPUT_JSON}\n  {OUTPUT_JSON_COPY}")


if __name__ == "__main__":
    main()
