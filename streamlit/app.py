import streamlit as st
from datetime import datetime

# =========================================================
# CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="Support Ticket Agent",
    page_icon="🎫",
    layout="wide"
)

# =========================================================
# PLACEHOLDER AGENT FUNCTIONS (À remplacer plus tard)
# =========================================================

def analyze_ticket(raw_text):
    """
    Agent 1-2-3-4 : Analyse (sentiment, urgence, routing)
    """
    return {
        "sentiment": None,
        "urgency": None,
        "department": None
    }


def retrieve_knowledge(clean_text, department):
    """
    RAG - Cortex Search
    """
    return []


def generate_response(raw_text, analysis, retrieved_docs):
    """
    Agent 5 - Génération
    """
    return ""


def evaluate_response(response):
    """
    Agent 6 - Validator
    """
    return {
        "quality_score": None,
        "safe_to_send": None,
        "issues": []
    }


# =========================================================
# INITIALISATION SESSION
# =========================================================

if "ticket_state" not in st.session_state:
    st.session_state.ticket_state = None


# =========================================================
# HEADER
# =========================================================

st.title("🎫 Multi-Agent Support Ticket System")
st.caption("Planning + Tool-Use + Gating Architecture")

st.divider()


# =========================================================
# SECTION 1 - INPUT TICKET
# =========================================================

st.subheader("1️⃣ Submit a Ticket")

ticket_text = st.text_area(
    "Customer Message",
    height=150,
    placeholder="Describe your issue..."
)

client_id = st.text_input("Client ID (optional)")

process = st.button("🚀 Process Ticket")


# =========================================================
# PIPELINE ORCHESTRATION
# =========================================================

if process and ticket_text:

    clean_text = ticket_text.lower()

    analysis = analyze_ticket(ticket_text)

    retrieved_docs = retrieve_knowledge(
        clean_text,
        analysis.get("department")
    )

    response = generate_response(
        ticket_text,
        analysis,
        retrieved_docs
    )

    evaluation = evaluate_response(response)

    st.session_state.ticket_state = {
        "raw_text": ticket_text,
        "clean_text": clean_text,
        "analysis": analysis,
        "retrieved_docs": retrieved_docs,
        "response": response,
        "evaluation": evaluation,
        "timestamp": str(datetime.now())
    }


# =========================================================
# SECTION 2 - DISPLAY RESULTS
# =========================================================

if st.session_state.ticket_state:

    state = st.session_state.ticket_state

    st.divider()
    st.subheader("2️⃣ Analysis")

    st.json(state["analysis"])

    st.divider()
    st.subheader("3️⃣ Retrieval")

    st.json(state["retrieved_docs"])

    st.divider()
    st.subheader("4️⃣ Generated Response")

    st.write(state["response"] or "⚠️ No response generated yet.")

    st.divider()
    st.subheader("5️⃣ Evaluation")

    st.json(state["evaluation"])

    st.divider()
    st.subheader("6️⃣ Feedback")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("👍 Helpful"):
            st.success("Feedback recorded (placeholder).")

    with col2:
        if st.button("👎 Not Helpful"):
            st.error("Feedback recorded (placeholder).")
