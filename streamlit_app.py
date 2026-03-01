import streamlit as st
from datetime import datetime
from agents.analyse_sentiment import detect_sentiment
from agents.analyse_priorite import determine_priority

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="AI Support System", layout="wide")

# =========================================================
# STYLE (pro + un peu de couleur)
# =========================================================
st.markdown("""
<style>
.block-container { padding-top: 2rem; max-width: 1200px; }

/* Pipeline */
.pipeline-wrap { display:flex; align-items:center; justify-content:center; gap:10px; margin-top:6px; }
.step { padding:10px 18px; border-radius:10px; font-size:13px; font-weight:700;
        background:#EEF2FF; color:#3730A3; border:1px solid #C7D2FE; }
.step.off { background:#F3F4F6; color:#374151; border:1px solid #E5E7EB; font-weight:600; }
.arrow { color:#9CA3AF; font-weight:800; }

/* Status badge */
.badge { display:inline-block; padding:6px 12px; border-radius:999px; font-size:12px; font-weight:700; }
.badge.active { background:#DBEAFE; color:#1D4ED8; }
.badge.escalated { background:#FEE2E2; color:#B91C1C; }
.badge.closed { background:#D1FAE5; color:#065F46; }

/* Cards */
.card { border:1px solid #E5E7EB; background:white; border-radius:12px; padding:16px; }
.kpi { border:1px solid #E5E7EB; background:#F9FAFB; border-radius:12px; padding:14px; text-align:center; }
.kpi .label { font-size:12px; color:#6B7280; font-weight:700; letter-spacing:.02em; }
.kpi .value { margin-top:6px; font-size:18px; font-weight:800; color:#111827; }

/* Buttons */
.stButton>button { background:#4F46E5; color:white; border-radius:10px; font-weight:650; }
.smallbtn .stButton>button { background:#111827; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# SESSION INIT
# =========================================================
if "tickets" not in st.session_state:
    st.session_state.tickets = []

if "selected_ticket_id" not in st.session_state:
    st.session_state.selected_ticket_id = None

# =========================================================
# NORMALIZE EXISTING TICKETS (avoid KeyError)
# =========================================================
def normalize_tickets():
    """
    Ensure every ticket has an integer 'id' and expected keys.
    This prevents crashes if previous runs stored older formats.
    """
    next_id = 1
    for t in st.session_state.tickets:
        if not isinstance(t, dict):
            continue
        if "id" not in t:
            t["id"] = next_id
        next_id = max(next_id, int(t.get("id", 0)) + 1)

normalize_tickets()

def next_ticket_id():
    if not st.session_state.tickets:
        return 1
    return max(int(t.get("id", 0)) for t in st.session_state.tickets if isinstance(t, dict)) + 1

# =========================================================
# LOGIC
# =========================================================
def analyze_ticket(raw_text):
    sentiment = detect_sentiment(raw_text)
    priority, confidence = determine_priority(raw_text, {"sentiment": sentiment})

    status = "Escalated" if str(priority).lower() in ["high", "critical"] else "Active"

    response = (
        "Thank you for contacting support.\n\n"
        "We have received your request and started the analysis.\n"
        "If we need additional information, we will get back to you.\n\n"
        "Best regards,\nSupport Team"
    )

    return {
        "sentiment": sentiment,
        "priority": priority,
        "confidence": float(confidence) if confidence is not None else 0.0,
        "status": status,
        "department": "IT Support",
        "response": response,
        "feedback": None,
    }

def get_selected_ticket():
    tid = st.session_state.selected_ticket_id
    if tid is None:
        return None
    for t in st.session_state.tickets:
        if isinstance(t, dict) and int(t.get("id", -1)) == int(tid):
            return t
    return None

# =========================================================
# HEADER
# =========================================================
st.title("AI Multi-Agent Support System")
st.caption("Structured Ticket Processing Workflow")
st.divider()

# =========================================================
# PIPELINE
# =========================================================
st.markdown("### Processing Pipeline")
st.markdown("""
<div class="pipeline-wrap">
  <div class="step">1. Sentiment</div>
  <div class="arrow">→</div>
  <div class="step">2. Priority</div>
  <div class="arrow">→</div>
  <div class="step">3. Routing</div>
</div>
""", unsafe_allow_html=True)

st.divider()

# =========================================================
# LAYOUT
# =========================================================
left, right = st.columns([1, 2], gap="large")

# =========================================================
# LEFT: NEW TICKET + HISTORY
# =========================================================
with left:
    st.subheader("New Ticket")
    ticket_text = st.text_area("Message", height=130, placeholder="Describe your issue...")
    client_id = st.text_input("Client ID (optional)")

    if st.button("Submit Ticket", use_container_width=True):
        if ticket_text.strip():
            with st.spinner("Processing ticket..."):
                result = analyze_ticket(ticket_text)

            ticket_data = {
                "id": next_ticket_id(),
                "client_id": client_id.strip(),
                "text": ticket_text.strip(),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                **result
            }
            st.session_state.tickets.append(ticket_data)
            st.session_state.selected_ticket_id = ticket_data["id"]
        else:
            st.warning("Please enter a message before submitting.")

    st.divider()
    st.subheader("Ticket History")

    if not st.session_state.tickets:
        st.caption("No tickets yet.")
    else:
        # show latest first
        for t in reversed(st.session_state.tickets):
            if not isinstance(t, dict):
                continue

            tid = t.get("id", "?")
            prio = t.get("priority", "N/A")
            status = t.get("status", "N/A")
            ts = t.get("timestamp", "")

            label = f"#{tid} • {prio} • {status}"
            if ts:
                label += f" • {ts}"

            # use stable key to avoid Streamlit button collisions
            if st.button(label, key=f"hist_{tid}", use_container_width=True):
                st.session_state.selected_ticket_id = tid

# =========================================================
# RIGHT: DETAILS
# =========================================================
with right:
    ticket = get_selected_ticket()

    if not ticket:
        st.info("Select a ticket from the history to view details.")
    else:
        st.subheader(f"Ticket #{ticket.get('id')} Details")

        status = ticket.get("status", "Active")
        badge_class = "active"
        if status == "Escalated":
            badge_class = "escalated"
        elif status == "Closed":
            badge_class = "closed"

        st.markdown(f'<span class="badge {badge_class}">{status}</span>', unsafe_allow_html=True)
        st.caption(f"Department: {ticket.get('department','N/A')} • Client: {ticket.get('client_id') or '—'}")

        st.markdown("#### Analysis")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""
            <div class="kpi">
              <div class="label">SENTIMENT</div>
              <div class="value">{ticket.get("sentiment","N/A")}</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="kpi">
              <div class="label">PRIORITY</div>
              <div class="value">{ticket.get("priority","N/A")}</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            conf = ticket.get("confidence", 0.0)
            try:
                conf = round(float(conf), 2)
            except Exception:
                conf = 0.0
            st.markdown(f"""
            <div class="kpi">
              <div class="label">CONFIDENCE</div>
              <div class="value">{conf}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("#### Generated Response")
        st.markdown(f'<div class="card" style="white-space:pre-line;">{ticket.get("response","")}</div>', unsafe_allow_html=True)

        st.markdown("#### Was this response helpful?")
        fb1, fb2, fb3 = st.columns([1, 1, 2])

        with fb1:
            if st.button("👍 Yes", key=f"fb_yes_{ticket['id']}"):
                ticket["feedback"] = "positive"
        with fb2:
            if st.button("👎 No", key=f"fb_no_{ticket['id']}"):
                ticket["feedback"] = "negative"

        if ticket.get("feedback"):
            st.success(f"Feedback recorded: {ticket['feedback']}")

        with st.expander("Technical JSON Output"):
            st.json(ticket)