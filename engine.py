# engine.py
# The INFERENCE ENGINE: it applies the rules to the symptoms the user selected.
# It uses forward chaining: start from the facts (symptoms) and move forward
# to conclusions (diagnoses).

from rules import RULES, CONFLICTS

MIN_MATCH = 0.66   # a rule fires if at least 66% of its conditions are present
MAX_CF = 0.99      # confidence is never allowed to reach 100%


def match_rule(rule, user_symptoms):
    """Split a rule's conditions into matched and missing symptoms."""
    matched = []
    missing = []
    for symptom in rule["if"]:
        if symptom in user_symptoms:
            matched.append(symptom)
        else:
            missing.append(symptom)
    return matched, missing


def combine_cf(old_cf, new_cf):
    """Combine two confidence values for the same diagnosis."""
    return old_cf + new_cf * (1 - old_cf)


def get_cf(result):
    """Helper used for sorting results by confidence."""
    return result["cf"]


def check_conflicts(user_symptoms):
    """Return the pairs of selected symptoms that contradict each other."""
    found = []
    for first, second in CONFLICTS:
        if first in user_symptoms and second in user_symptoms:
            found.append((first, second))
    return found


def confidence_label(cf):
    """Turn a number into a word: High, Medium or Low."""
    if cf >= 0.80:
        return "High"
    if cf >= 0.60:
        return "Medium"
    return "Low"


def run_inference(user_symptoms):
    """Apply all rules and return a list of diagnoses (best first)."""
    # Step 1: find every rule that fires
    fired_rules = []
    for rule in RULES:
        matched, missing = match_rule(rule, user_symptoms)
        fraction = len(matched) / len(rule["if"])
        if len(matched) > 0 and fraction >= MIN_MATCH:
            fired_rules.append({
                "rule": rule,
                "matched": matched,
                "missing": missing,
                "fraction": fraction,
                "cf": rule["cf"] * fraction,   # fewer matches = lower confidence
                "cf_after": 0.0,
            })

    # Step 2: group the fired rules by diagnosis and combine their confidence
    diagnoses = {}
    for item in fired_rules:
        name = item["rule"]["then"]
        if name not in diagnoses:
            diagnoses[name] = {
                "diagnosis": name,
                "category": item["rule"]["category"],
                "advice": item["rule"]["advice"],
                "cf": 0.0,
                "fired": [],
            }
        current = diagnoses[name]
        new_cf = combine_cf(current["cf"], item["cf"])
        if new_cf > MAX_CF:
            new_cf = MAX_CF
        current["cf"] = new_cf
        item["cf_after"] = new_cf
        current["fired"].append(item)

    # Step 3: sort so the most likely diagnosis is first
    results = list(diagnoses.values())
    results.sort(key=get_cf, reverse=True)
    return results


def find_followups(user_symptoms, results):
    """Decision support: which extra symptoms would make another diagnosis possible?"""
    already_found = []
    for result in results:
        already_found.append(result["diagnosis"])

    suggestions = []
    for rule in RULES:
        matched, missing = match_rule(rule, user_symptoms)
        fraction = len(matched) / len(rule["if"])
        if len(matched) > 0 and fraction < MIN_MATCH:
            if rule["then"] not in already_found:
                suggestions.append({"diagnosis": rule["then"], "check": missing, "cf": rule["cf"]})
                already_found.append(rule["then"])

    suggestions.sort(key=get_cf, reverse=True)
    return suggestions[:5]
