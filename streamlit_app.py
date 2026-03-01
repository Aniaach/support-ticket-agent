import streamlit as st
from datetime import datetime
from agents.analyse_sentiment import detect_sentiment
from agents.analyse_priorite import determine_priority

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="AI Support Ticket System",
    page_icon="🎫",
    layout="wide"
)

# =========================================================
# STYLE MINIMALISTE PRO
# =========================================================
st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
.stTextArea textarea {
    border-radius: 10px;
    font-size: 15px;
}
.stTextInput input {
    border-radius: 8px;
}
.stButton>button {
    border-radius: 8px;
    background-color: #4F46E5;
    color: white;
    font-weight: 600;
    padding: 0.6em 1.2em;
}
.metric-card {
    background-color: #F9FAFB;
    padding: 18px;
    border-radius: 12px;
    text-align: center;
}
.pipeline-step {
    text-align: center;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# SESSION
# =========================================================
if "ticket_state" not in st.session_state:
    st.session_state.ticket_state = None

# =========================================================
# ORCHESTRATION
# =========================================================
def analyze_ticket(raw_text):
    sentiment = detect_sentiment(raw_text)
    analysis_obj = {"sentiment": sentiment}
    priority, confidence = determine_priority(raw_text, analysis_obj)

    return {
        "sentiment": sentiment,
        "priority": priority,
        "confidence": confidence,
        "department": "IT Support"
    }

# =========================================================
# HEADER
# =========================================================
st.title("🎫 AI Multi-Agent Support System")
st.caption("Structured Agent Pipeline with Controlled Decision Flow")
st.divider()

# =========================================================
# PIPELINE VISUELLE
# =========================================================
st.markdown("### 🔎 Processing Pipeline")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("🧠 **Sentiment Analysis**")
with col2:
    st.markdown("⚡ **Priority Scoring**")
with col3:
    st.markdown("📂 **Routing**")

st.progress(1.0)

st.divider()

# =========================================================
# LAYOUT PRINCIPAL
# =========================================================
left, right = st.columns([1.2, 1])

# =========================================================
# INPUT PANEL
# =========================================================
with left:
    st.subheader("Submit a Ticket")

    ticket_text = st.text_area(
        "Customer Message",
        height=200,
        placeholder="Describe your issue..."
    )

    client_id = st.text_input("Client ID (optional)")

    process = st.button("🚀 Process Ticket", use_container_width=True)

    if process and ticket_text:
        with st.spinner("Analyzing ticket..."):
            analysis = analyze_ticket(ticket_text)

            st.session_state.ticket_state = {
                "raw_text": ticket_text,
                "analysis": analysis,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

# =========================================================
# RESULT PANEL
# =========================================================
with right:
    st.subheader("Analysis Result")

    if st.session_state.ticket_state:
        state = st.session_state.ticket_state
        analysis = state["analysis"]

        sentiment_color = {
            "positive": "🟢",
            "neutral": "🟡",
            "negative": "🔴"
        }.get(analysis["sentiment"].lower(), "⚪")

        priority_color = {
            "low": "🟢",
            "medium": "🟡",
            "high": "🔴",
            "critical": "🔥"
        }.get(analysis["priority"].lower(), "⚪")

        st.markdown(f"""
        <div class="metric-card">
            <h4>Sentiment</h4>
            <p style="font-size:20px">{sentiment_color} {analysis['sentiment']}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="metric-card">
            <h4>Priority</h4>
            <p style="font-size:20px">{priority_color} {analysis['priority']}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="metric-card">
            <h4>Confidence</h4>
            <p style="font-size:20px">{round(analysis['confidence'],2)}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.info(f"📂 Routed to: {analysis['department']}")

        with st.expander("Technical JSON Output"):
            st.json(state)

    else:
        st.info("No ticket processed yet.")