# app.py
# The Streamlit user interface. Run with:  streamlit run app.py

import streamlit as st

from rules import RULES, SYMPTOMS, CATEGORIES, URGENT_DIAGNOSES
from engine import run_inference, check_conflicts, find_followups, confidence_label
from decision_tree import follow_path, is_leaf
from explain import explain_result, explain_path, nice, percent

st.set_page_config(page_title="Laptop Troubleshooting Expert System", page_icon="L", layout="wide")

st.markdown("""
<style>
    .block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1100px; }
    div[data-testid="stExpander"] { border: 1px solid rgba(128, 128, 128, 0.28); border-radius: 4px; }
    div[data-testid="stProgressBar"] { margin: 0.35rem 0 0.75rem; }
</style>
""", unsafe_allow_html=True)


def show_results(user_symptoms):
    """Run the inference engine and display the diagnoses on the page."""
    results = run_inference(user_symptoms)

    if len(results) == 0:
        st.warning("No rule matched these symptoms. Try selecting more symptoms "
                   "or use the guided decision tree.")
        return

    st.subheader("Diagnosis results")
    top = results[0]
    st.success("Most likely problem: **" + top["diagnosis"] + "** (" + percent(top["cf"]) + " confidence)")

    # show at most 5 diagnoses
    for number, result in enumerate(results[:5], start=1):
        st.markdown("### " + str(number) + ". " + result["diagnosis"])
        if result["diagnosis"] in URGENT_DIAGNOSES:
            st.error("URGENT: " + result["advice"])
        st.progress(result["cf"])
        st.caption("Confidence: " + percent(result["cf"]) + " (" + confidence_label(result["cf"])
                   + ")  |  Category: " + result["category"])
        st.write("**Recommended action:** " + result["advice"])
        with st.expander("Why did the system say this?"):
            st.markdown(explain_result(result))

    # decision support: extra things to check
    followups = find_followups(user_symptoms, results)
    if len(followups) > 0:
        st.subheader("Things to check next")
        st.caption("If you notice these as well, other diagnoses become possible:")
        for item in followups:
            names = ", ".join([nice(s) for s in item["check"]])
            st.write("- **" + item["diagnosis"] + "** becomes possible if: " + names)

    st.info("This system gives suggestions, not guarantees. For serious or hardware problems "
            "please consult a technician.")


def clear_all_symptoms():
    """Untick every symptom checkbox (used by the Clear button)."""
    for symptom in SYMPTOMS:
        st.session_state[symptom] = False


# ---------------- Sidebar ----------------
st.sidebar.title("Laptop Expert System")
st.sidebar.caption("Troubleshoot common computer problems")
page = st.sidebar.radio("Choose a mode", [
    "Symptom Checker",
    "Guided Diagnosis (Decision Tree)",
    "Rule Base",
])
st.sidebar.caption(str(len(RULES)) + " rules | forward chaining | certainty factors")

# ---------------- Page 1: Symptom Checker ----------------
if page == "Symptom Checker":
    st.title("Computer & Laptop Troubleshooting Expert System")
    st.write("Select all symptoms that apply, then choose **Diagnose** to see likely causes and recommended actions.")

    selected = []
    for category in CATEGORIES:
        category_symptoms = [symptom for symptom in SYMPTOMS if SYMPTOMS[symptom][0] == category]
        category_selected = sum(bool(st.session_state.get(symptom, False)) for symptom in category_symptoms)
        with st.expander(category + "  ·  " + str(category_selected) + " selected"):
            for symptom in SYMPTOMS:
                if SYMPTOMS[symptom][0] == category:
                    if st.checkbox(SYMPTOMS[symptom][1], key=symptom):
                        selected.append(symptom)

    st.write("Selected symptoms: **" + str(len(selected)) + "**")
    col1, col2 = st.columns([1, 6])
    diagnose_clicked = col1.button("Diagnose", type="primary")
    col2.button("Clear all", on_click=clear_all_symptoms)

    if diagnose_clicked:
        conflicts = check_conflicts(selected)
        if len(selected) == 0:
            st.warning("Please select at least one symptom.")
        elif len(conflicts) > 0:
            for first, second in conflicts:
                st.error("These two cannot both be true: '" + nice(first) + "' and '" + nice(second) + "'.")
        else:
            show_results(selected)

# ---------------- Page 2: Decision Tree ----------------
elif page == "Guided Diagnosis (Decision Tree)":
    st.title("Guided Diagnosis (Decision Tree)")
    st.write("Answer each question based on what you observe. Your answers narrow down the likely problem.")

    if "tree_path" not in st.session_state:
        st.session_state["tree_path"] = []

    node, tree_symptoms, steps = follow_path(st.session_state["tree_path"])

    if len(steps) > 0:
        st.markdown("**Your answers so far:**")
        st.markdown(explain_path(steps))
        st.divider()

    if not is_leaf(node):
        st.subheader(node["question"])
        col1, col2, _ = st.columns([1, 1, 6])
        if col1.button("Yes"):
            st.session_state["tree_path"].append("yes")
            st.rerun()
        if col2.button("No"):
            st.session_state["tree_path"].append("no")
            st.rerun()
    else:
        st.success("Tree conclusion: " + node["result"])
        st.write("Problem area: **" + node["category"] + "**")
        if len(tree_symptoms) > 0:
            st.markdown("---")
            st.write("The answers you gave were turned into symptoms and sent to the inference engine:")
            show_results(tree_symptoms)

    if st.button("Start over"):
        st.session_state["tree_path"] = []
        st.rerun()

# ---------------- Page 3: Rule Base ----------------
else:
    st.title("Rule Base")
    st.write("All " + str(len(RULES)) + " IF-THEN rules used by the system.")
    table = []
    for rule in RULES:
        table.append({
            "ID": rule["id"],
            "Category": rule["category"],
            "IF (symptoms)": " AND ".join(rule["if"]),
            "THEN (diagnosis)": rule["then"],
            "Confidence": rule["cf"],
        })
    st.dataframe(table, use_container_width=True, hide_index=True)

