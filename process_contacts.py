import csv
import json
import re
import sys

# Tier 1 VC patterns using word boundaries for precise matching
TIER_1_VC_PATTERNS = [
    r"\bsequoia\b", r"\bandreessen horowitz\b", r"\ba16z\b",
    r"\bkleiner perkins\b", r"\blightspeed\b", r"\binsight partners\b",
    r"\bnew enterprise associates\b", r"\bnea\b",
    r"^founders fund\b", r"\bbessemer venture partners\b",
    r"\bgreylock\b", r"\bgeneral catalyst\b", r"\bunion square ventures\b",
    r"\bbenchmark\b", r"\bindex ventures\b", r"\btiger global\b",
    r"\bsoftbank\b", r"\bkhosla ventures\b", r"\bbattery ventures\b",
    r"\bivp\b", r"\binstitutional venture partners\b",
    r"\bmenlo ventures\b", r"\bredpoint ventures\b", r"\bspark capital\b",
    r"\bgv\b", r"\bgoogle ventures\b", r"\bnorwest venture partners\b",
    r"\bcoatue\b", r"\bribbit capital\b", r"\bthrive capital\b",
    r"\baccel\b",
]
# Compile patterns
TIER_1_RE = [re.compile(p, re.IGNORECASE) for p in TIER_1_VC_PATTERNS]

ACCELERATOR_KEYWORDS = ["accelerator", "incubator", "techstars", "y combinator", "ycombinator", "500 startups", "500 global", "launchpad", "startup lab"]
ANGEL_KEYWORDS = ["angel", "family office", "family fund", "individual investor"]

def categorize(fund_name, original_category):
    """Categorize a contact based on fund_name and original_category."""
    combined = (fund_name + " " + original_category).lower()

    # Check for Accelerator first
    for kw in ACCELERATOR_KEYWORDS:
        if kw in combined:
            return "Accelerator"

    # Check for Angel/Family Office
    for kw in ANGEL_KEYWORDS:
        if kw in combined:
            return "Angel/Family Office"

    # Check for Tier 1 VC using word-boundary regex
    fund_lower = fund_name.lower()
    for pattern in TIER_1_RE:
        if pattern.search(fund_lower):
            return "Tier 1 VC"

    # Default to Tier 2 VC
    return "Tier 2 VC"


def main():
    input_path = "/home/user/attachments/vcs-and-angels.csv"
    output_path = "/home/user/output/categorized_contacts.json"

    contacts_by_category = {}

    with open(input_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            fund_name = (row.get("name") or "").strip()
            contact_name = (row.get("contact") or "").strip()
            email = (row.get("email") or "").strip()

            # 'name' in output = person's name from 'contact' column
            name = contact_name

            # original_category: use contact column value if present, else derive from fund_name
            if contact_name:
                original_category = contact_name
            else:
                original_category = fund_name

            # Determine identified_category using heuristics
            identified_category = categorize(fund_name, original_category)

            missing_email = (email == "")

            contact_obj = {
                "name": name,
                "email": email,
                "fund_name": fund_name,
                "original_category": original_category,
                "identified_category": identified_category,
                "missing_email": missing_email,
                "potential_aman_overlap": False
            }

            if identified_category not in contacts_by_category:
                contacts_by_category[identified_category] = []
            contacts_by_category[identified_category].append(contact_obj)

    # Print summary
    total = sum(len(v) for v in contacts_by_category.values())
    print(f"Total contacts processed: {total}")
    for cat, contacts in sorted(contacts_by_category.items()):
        missing = sum(1 for c in contacts if c["missing_email"])
        print(f"  {cat}: {len(contacts)} contacts ({missing} missing email)")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(contacts_by_category, f, indent=2, ensure_ascii=False)

    print(f"\nOutput written to: {output_path}")


if __name__ == "__main__":
    main()
