"""Transparent keyword baseline for exploratory grouping; not a clinical classifier."""
import re

RULES = {
    "slip_or_trip": r"\b(slipped|slip|tripped|trip|stumbled|misstep|missed step)\b",
    "fall_from_bed_or_furniture": r"\b(bed|chair|couch|sofa|recliner|furniture)\b.*\b(fell|fall|slipped|rolled)\b|\b(fell|fall)\b.*\b(bed|chair|couch|sofa|recliner)\b",
    "stairs_or_steps": r"\b(stairs|staircase|steps|step stool|ladder)\b",
    "loss_of_balance": r"\b(lost balance|loss of balance|unsteady|balance)\b",
    "other_keyword_candidate": r"\b(fall|falls|fell|fallen|falling|tumble|tumbled)\b",
}

def assign_baseline_group(text: str) -> str:
    text = str(text or "").lower()
    for label, pattern in RULES.items():
        if re.search(pattern, text):
            return label
    return "no_rule_match"
