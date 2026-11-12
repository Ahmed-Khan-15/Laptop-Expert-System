# explain.py
# The EXPLANATION part: tells the user WHY the system gave a diagnosis.

from rules import SYMPTOMS
from engine import confidence_label


def nice(symptom):
    """Get the readable text of a symptom."""
    return SYMPTOMS[symptom][1]


def percent(value):
    """Turn 0.7 into '70%'."""
    return str(round(value * 100)) + "%"


def explain_result(result):
    """Build the explanation text (markdown) for one diagnosis."""
    lines = []
    lines.append("**Diagnosis:** " + result["diagnosis"])
    lines.append("")
    lines.append("**Rules that led to this conclusion:**")

    for item in result["fired"]:
        rule = item["rule"]
        lines.append("")
        lines.append("- **" + rule["id"] + "**: IF " + " AND ".join(rule["if"]) + " THEN " + rule["then"])
        lines.append("  - You reported: " + ", ".join([nice(s) for s in item["matched"]]))
        if len(item["missing"]) > 0:
            lines.append("  - You did not report: " + ", ".join([nice(s) for s in item["missing"]]))
            lines.append("  - So only part of the rule matched (" + percent(item["fraction"])
                         + "), and its confidence was reduced from " + percent(rule["cf"])
                         + " to " + percent(item["cf"]) + ".")
        else:
            lines.append("  - All conditions matched, so the rule confidence is " + percent(rule["cf"]) + ".")
        lines.append("  - Confidence for this diagnosis so far: " + percent(item["cf_after"]))

    lines.append("")
    if len(result["fired"]) > 1:
        lines.append("Several rules pointed to the same diagnosis, so their confidence values were "
                     "combined using: CF = CF1 + CF2 x (1 - CF1).")
    lines.append("**Final confidence:** " + percent(result["cf"]) + " (" + confidence_label(result["cf"])
                 + "). The system never claims 100% because symptoms can have more than one cause.")
    return "\n".join(lines)


def explain_path(steps):
    """Explain the questions and answers used in the decision tree."""
    lines = []
    number = 1
    for question, answer in steps:
        lines.append(str(number) + ". " + question + " -> **" + answer.upper() + "**")
        number = number + 1
    return "\n".join(lines)
