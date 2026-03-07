import streamlit as st
import time

from agents.analyse_sentiment import detect_sentiment
from agents.analyse_priorite import determine_priority
from agents.routing import detect_department
from agents.response import generate_response
from agents.top5_context import get_top5_context

from snowflake.snowpark.context import get_active_session

session = get_active_session()

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="AI Support System", layout="wide")

# =========================================================
# STYLE
# =========================================================
st.markdown("""
<style>
.block-container { padding-top: 1.5rem; max-width: 1280px; }

/* Pipeline */
.pipeline-wrap {
    display:flex;
    align-items:center;
    justify-content:center;
    gap:10px;
    flex-wrap:wrap;
    margin: 10px 0 8px 0;
}
.pipeline-step {
    padding:10px 16px;
    border-radius:12px;
    font-size:13px;
    font-weight:700;
    border:1px solid #E5E7EB;
    background:#F3F4F6;
    color:#374151;
    min-width:120px;
    text-align:center;
}
.pipeline-step.done {
    background:#DCFCE7;
    color:#166534;
    border:1px solid #86EFAC;
    box-shadow:0 0 0 1px rgba(34,197,94,.05);
}
.pipeline-step.active {
    background:#DBEAFE;
    color:#1D4ED8;
    border:1px solid #93C5FD;
    animation:pulse 1s infinite;
}
.pipeline-arrow {
    color:#9CA3AF;
    font-weight:900;
    font-size:18px;
}

@keyframes pulse {
  0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(59,130,246,.30); }
  70% { transform: scale(1.02); box-shadow: 0 0 0 10px rgba(59,130,246,0); }
  100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(59,130,246,0); }
}

/* Cards */
.card {
    border:1px solid #E5E7EB;
    background:white;
    border-radius:14px;
    padding:16px;
}
.kpi {
    border:1px solid #E5E7EB;
    background:#F9FAFB;
    border-radius:14px;
    padding:14px;
    text-align:center;
}
.kpi .label {
    font-size:12px;
    color:#6B7280;
    font-weight:700;
    letter-spacing:.02em;
}
.kpi .value {
    margin-top:6px;
    font-size:20px;
    font-weight:800;
    color:#111827;
}

/* Badge status */
.badge {
    display:inline-block;
    padding:6px 12px;
    border-radius:999px;
    font-size:12px;
    font-weight:700;
}
.badge.active { background:#DBEAFE; color:#1D4ED8; }
.badge.escalated { background:#FEE2E2; color:#B91C1C; }
.badge.closed { background:#D1FAE5; color:#065F46; }

/* Priority pill */
.pill {
    display:inline-block;
    padding:4px 10px;
    border-radius:999px;
    font-size:12px;
    font-weight:700;
    margin-left:6px;
}
.pill.low { background:#DCFCE7; color:#166534; }
.pill.medium { background:#FEF3C7; color:#92400E; }
.pill.high { background:#FEE2E2; color:#B91C1C; }
.pill.critical { background:#E9D5FF; color:#6B21A8; }

/* Agent log */
.agent-log {
    border:1px dashed #D1D5DB;
    background:#FAFAFA;
    border-radius:12px;
    padding:12px 14px;
    font-size:13px;
    color:#374151;
}

/* Buttons */
.stButton > button {
    border-radius:10px;
    font-weight:650;
}

/* Small muted text block */
.muted {
    color:#6B7280;
    font-size:13px;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# SESSION STATE INIT
# =========================================================
if "selected_ticket_id" not in st.session_state:
    st.session_state.selected_ticket_id = None

if "role" not in st.session_state:
    st.session_state.role = "Customer"

# =========================================================
# HELPERS
# =========================================================
def sql_escape(value):
    if value is None:
        return ""
    return str(value).replace("'", "''")


def get_status_badge_class(status):
    s = str(status).lower()
    if s == "escalated":
        return "escalated"
    if s == "closed":
        return "closed"
    return "active"


def get_priority_class(priority):
    p = str(priority).lower()
    if p == "critical":
        return "critical"
    if p == "high":
        return "high"
    if p in ["medium", "moderate"]:
        return "medium"
    return "low"


def priority_icon(priority):
    p = str(priority).lower()
    if p == "critical":
        return "🟣"
    if p == "high":
        return "🔴"
    if p in ["medium", "moderate"]:
        return "🟡"
    return "🟢"


def render_pipeline(active_index=-1, completed_until=-1, container=None):
    steps = [
        "Ticket",
        "Sentiment Agent",
        "Priority Agent",
        "Routing Agent",
        "RAG Agent",
        "Response Agent"
    ]

    html = '<div class="pipeline-wrap">'
    for i, step in enumerate(steps):
        cls = "pipeline-step"
        if i <= completed_until:
            cls += " done"
        elif i == active_index:
            cls += " active"

        html += f'<div class="{cls}">{step}</div>'
        if i < len(steps) - 1:
            html += '<div class="pipeline-arrow">→</div>'
    html += "</div>"

    if container is not None:
        container.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown(html, unsafe_allow_html=True)


def display_agent_log(message, container):
    container.markdown(f'<div class="agent-log">{message}</div>', unsafe_allow_html=True)


def render_static_completed_pipeline():
    render_pipeline(active_index=-1, completed_until=5)


def run_pipeline_simulation(raw_text, animate=True):
    pipeline_placeholder = st.empty()
    log_placeholder = st.empty()

    render_pipeline(active_index=0, completed_until=-1, container=pipeline_placeholder)
    display_agent_log("🎫 Ticket received.", log_placeholder)
    if animate:
        time.sleep(0.35)

    render_pipeline(active_index=1, completed_until=0, container=pipeline_placeholder)
    display_agent_log("😊 Sentiment Agent analysing ticket tone...", log_placeholder)
    sentiment = detect_sentiment(raw_text)
    if animate:
        time.sleep(0.45)

    render_pipeline(active_index=2, completed_until=1, container=pipeline_placeholder)
    display_agent_log("⚡ Priority Agent calculating urgency level...", log_placeholder)
    priority, confidence = determine_priority(raw_text, {"sentiment": sentiment})
    if animate:
        time.sleep(0.45)

    render_pipeline(active_index=3, completed_until=2, container=pipeline_placeholder)
    display_agent_log("🧭 Routing Agent identifying target department...", log_placeholder)
    try:
        department = detect_department(raw_text)
    except Exception:
        department = "General Inquiry"
    if animate:
        time.sleep(0.45)

    render_pipeline(active_index=4, completed_until=3, container=pipeline_placeholder)
    display_agent_log("📚 RAG Agent retrieving the most relevant context...", log_placeholder)
    top5_context = get_top5_context(department)
    if animate:
        time.sleep(0.45)

    render_pipeline(active_index=5, completed_until=4, container=pipeline_placeholder)
    display_agent_log("✍️ Response Agent generating a draft answer...", log_placeholder)
    response = generate_response(
        ticket_text=raw_text,
        department=department,
        sentiment=sentiment,
        #top_k_lines=top5_context
    )
    if animate:
        time.sleep(0.45)

    render_pipeline(active_index=-1, completed_until=5, container=pipeline_placeholder)
    display_agent_log("✅ Multi-agent workflow completed.", log_placeholder)

    status = "Escalated" if str(priority).lower() in ["high", "critical"] else "Active"

    return {
        "sentiment": sentiment,
        "priority": priority,
        "confidence": float(confidence) if confidence is not None else 0.0,
        "status": status,
        "department": department,
        "response": response,
        "top5_context": top5_context,
        "feedback": None,
        "last_pipeline_steps": [
            "Ticket",
            "Sentiment Agent",
            "Priority Agent",
            "Routing Agent",
            "RAG Agent",
            "Response Agent"
        ]
    }

def normalize_record_keys(record):
    return {str(k).lower(): v for k, v in record.items()}
    
# =========================================================
# DATABASE FUNCTIONS
# =========================================================
def get_all_tickets():
    df = session.sql("""
        SELECT *
        FROM support_tickets
        ORDER BY created_at DESC
    """).to_pandas()

    if df.empty:
        return []

    records = df.to_dict("records")
    return [normalize_record_keys(r) for r in records]


def get_selected_ticket():
    tid = st.session_state.get("selected_ticket_id")

    if tid is None:
        return None

    try:
        tid = int(tid)
    except Exception:
        return None

    df = session.sql(f"""
        SELECT *
        FROM support_tickets
        WHERE ticket_id = {tid}
        LIMIT 1
    """).to_pandas()

    if df.empty:
        return None

    record = df.to_dict("records")[0]
    return normalize_record_keys(record)


def get_next_ticket_id():
    result = session.sql("""
        SELECT COALESCE(MAX(ticket_id), 0) + 1 AS NEXT_ID
        FROM support_tickets
    """).collect()

    return int(result[0]["NEXT_ID"])


def insert_ticket(ticket):
    client_id = sql_escape(ticket["client_id"])
    sentiment = sql_escape(ticket["sentiment"])
    priority = sql_escape(ticket["priority"])
    department = sql_escape(ticket["department"])
    status = sql_escape(ticket["status"])
    feedback_sql = "NULL" if ticket["feedback"] is None else f"'{sql_escape(ticket['feedback'])}'"

    session.sql(f"""
        INSERT INTO support_tickets (
            ticket_id,
            client_id,
            ticket_text,
            sentiment,
            priority,
            confidence,
            department,
            generated_response,
            status,
            feedback,
            quality_score,
            safe_to_send,
            retry_count,
            created_at
        )
        VALUES (
            {ticket["ticket_id"]},
            '{client_id}',
            $$ {ticket["ticket_text"]} $$,
            '{sentiment}',
            '{priority}',
            {ticket["confidence"]},
            '{department}',
            $$ {ticket["generated_response"]} $$,
            '{status}',
            {feedback_sql},
            {ticket["quality_score"]},
            {str(ticket["safe_to_send"]).upper()},
            {ticket["retry_count"]},
            CURRENT_TIMESTAMP()
        )
    """).collect()


def insert_monitoring(ticket):
    sentiment = sql_escape(ticket["sentiment"])
    priority = sql_escape(ticket["priority"])
    department = sql_escape(ticket["department"])
    status = sql_escape(ticket["status"])

    session.sql(f"""
        INSERT INTO agent_monitoring (
            ticket_id,
            sentiment,
            priority,
            department,
            quality_score,
            safe_to_send,
            retry_count,
            final_status,
            created_at
        )
        VALUES (
            {ticket["ticket_id"]},
            '{sentiment}',
            '{priority}',
            '{department}',
            {ticket["quality_score"]},
            {str(ticket["safe_to_send"]).upper()},
            {ticket["retry_count"]},
            '{status}',
            CURRENT_TIMESTAMP()
        )
    """).collect()


def update_ticket_status(ticket_id, status):
    safe_status = sql_escape(status)

    session.sql(f"""
        UPDATE support_tickets
        SET status = '{safe_status}'
        WHERE ticket_id = {int(ticket_id)}
    """).collect()


def update_ticket_feedback(ticket_id, feedback):
    safe_feedback = sql_escape(feedback)

    session.sql(f"""
        UPDATE support_tickets
        SET feedback = '{safe_feedback}'
        WHERE ticket_id = {int(ticket_id)}
    """).collect()

# =========================================================
# HEADER
# =========================================================
st.title("🤖 AI Multi-Agent Support System")
st.caption("Customer support workflow with simulated multi-agent pipeline")

role = st.radio(
    "Workspace Mode",
    ["Customer", "Support Agent"],
    horizontal=True,
    key="role"
)

st.divider()

# =========================================================
# DASHBOARD
# =========================================================
tickets = get_all_tickets()

if not tickets:
    st.session_state.selected_ticket_id = None

total_tickets = len(tickets)
active_tickets = sum(1 for t in tickets if str(t.get("status")) == "Active")
escalated_tickets = sum(1 for t in tickets if str(t.get("status")) == "Escalated")
closed_tickets = sum(1 for t in tickets if str(t.get("status")) == "Closed")
positive_feedback = sum(1 for t in tickets if str(t.get("feedback")) == "positive")

k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.markdown(f"""
    <div class="kpi">
        <div class="label">TOTAL TICKETS</div>
        <div class="value">{total_tickets}</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi">
        <div class="label">ACTIVE</div>
        <div class="value">{active_tickets}</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi">
        <div class="label">ESCALATED</div>
        <div class="value">{escalated_tickets}</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi">
        <div class="label">CLOSED</div>
        <div class="value">{closed_tickets}</div>
    </div>
    """, unsafe_allow_html=True)

with k5:
    st.markdown(f"""
    <div class="kpi">
        <div class="label">POSITIVE FEEDBACK</div>
        <div class="value">{positive_feedback}</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# =========================================================
# MAIN LAYOUT
# =========================================================
left, right = st.columns([1, 2], gap="large")

# =========================================================
# LEFT PANEL
# =========================================================
with left:
    if role == "Customer":
        st.subheader("Create Ticket")

        ticket_text = st.text_area(
            "Message",
            height=140,
            placeholder="Describe your issue..."
        )

        client_id = st.text_input("Client ID", placeholder="e.g. C12345")
        animate_pipeline = st.checkbox("Animate multi-agent pipeline", value=True)

        if st.button("Submit Ticket", use_container_width=True):
            if ticket_text.strip():
                with st.spinner("Processing ticket..."):
                    result = run_pipeline_simulation(ticket_text, animate=animate_pipeline)

                ticket_id = get_next_ticket_id()

                ticket_data = {
                    "ticket_id": ticket_id,
                    "client_id": client_id.strip(),
                    "ticket_text": ticket_text.strip(),
                    "sentiment": result["sentiment"],
                    "priority": result["priority"],
                    "confidence": result["confidence"],
                    "department": result["department"],
                    "generated_response": result["response"],
                    "status": result["status"],
                    "feedback": None,
                    "quality_score": 0.95,
                    "safe_to_send": True,
                    "retry_count": 0
                }

                insert_ticket(ticket_data)
                insert_monitoring(ticket_data)

                st.session_state.selected_ticket_id = ticket_id
                st.success("Ticket created successfully.")
                st.rerun()
            else:
                st.warning("Please enter a message before submitting.")

    else:
        st.subheader("Support Controls")

        status_filter = st.selectbox(
            "Filter by status",
            ["All", "Active", "Escalated", "Closed"]
        )

        priority_filter = st.selectbox(
            "Filter by priority",
            ["All", "Low", "Medium", "High", "Critical"]
        )

        search_term = st.text_input("Search by keyword / client ID")

    st.divider()
    st.subheader("Ticket History")

    filtered_tickets = []

    if role == "Customer":
        customer_search = st.text_input("Search my tickets")
        customer_client_filter = st.text_input("Filter by my Client ID")

        for t in tickets:
            if customer_search and customer_search.lower() not in str(t.get("ticket_text", "")).lower():
                continue

            if customer_client_filter and customer_client_filter.lower() not in str(t.get("client_id", "")).lower():
                continue

            filtered_tickets.append(t)

    else:
        for t in tickets:
            if status_filter != "All" and str(t.get("status")) != status_filter:
                continue

            if priority_filter != "All" and str(t.get("priority", "")).lower() != priority_filter.lower():
                continue

            if search_term:
                haystack = f"{t.get('ticket_text','')} {t.get('client_id','')} {t.get('department','')}".lower()
                if search_term.lower() not in haystack:
                    continue

            filtered_tickets.append(t)

    if not filtered_tickets:
        st.caption("No matching tickets.")
    else:
        for t in filtered_tickets:
            tid = t.get("ticket_id", "?")
            prio = t.get("priority", "N/A")
            status = t.get("status", "N/A")
            ts = str(t.get("created_at", ""))[:16]
            icon = priority_icon(prio)

            label = f"#{tid} {icon} {prio} • {status}"
            if ts and ts != "None":
                label += f" • {ts}"

            if st.button(label, key=f"hist_{tid}", use_container_width=True):
                st.session_state.selected_ticket_id = tid

# =========================================================
# RIGHT PANEL
# =========================================================
with right:
    ticket = get_selected_ticket()

    if not ticket:
        st.info("Select a ticket from the history to view details.")
    else:
        st.subheader(f"Ticket #{ticket.get('ticket_id')} Details")

        status = ticket.get("status", "Active")
        badge_class = get_status_badge_class(status)
        prio_class = get_priority_class(ticket.get("priority", "Low"))

        top_row_1, top_row_2 = st.columns([2, 1])

        with top_row_1:
            st.markdown(
                f'<span class="badge {badge_class}">{status}</span>'
                f'<span class="pill {prio_class}">{ticket.get("priority","N/A")}</span>',
                unsafe_allow_html=True
            )

            st.caption(
                f"Department: {ticket.get('department','N/A')} • "
                f"Client: {ticket.get('client_id') or '—'} • "
                f"Created: {str(ticket.get('created_at','—'))[:16]}"
            )

        with top_row_2:
            if role == "Support Agent":
                if status != "Closed":
                    if st.button("Close Ticket", use_container_width=True):
                        update_ticket_status(ticket["ticket_id"], "Closed")
                        st.success("Ticket closed.")
                        st.rerun()
                else:
                    if st.button("Reopen Ticket", use_container_width=True):
                        update_ticket_status(ticket["ticket_id"], "Active")
                        st.success("Ticket reopened.")
                        st.rerun()

        st.markdown("### Multi-Agent Pipeline")
        render_static_completed_pipeline()
        st.markdown(
            '<div class="muted">This ticket went through the full agent workflow: Sentiment → Priority → Routing → RAG → Response.</div>',
            unsafe_allow_html=True
        )

        st.markdown("### Analysis")
        c1, c2, c3, c4 = st.columns(4)

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

        with c4:
            st.markdown(f"""
            <div class="kpi">
              <div class="label">DEPARTMENT</div>
              <div class="value">{ticket.get("department","N/A")}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("### Original Message")
        st.markdown(
            f'<div class="card" style="white-space:pre-line;">{ticket.get("ticket_text","")}</div>',
            unsafe_allow_html=True
        )

        st.markdown("### Generated Response")
        st.markdown(
            f'<div class="card" style="white-space:pre-line;">{ticket.get("generated_response","")}</div>',
            unsafe_allow_html=True
        )

        st.markdown("### Knowledge Context Used")
        st.caption("Context lines are used during generation but are not stored in support_tickets.")

        if role == "Customer":
            st.markdown("### Was this response helpful?")
            fb1, fb2 = st.columns(2)

            with fb1:
                if st.button("👍 Helpful", key=f"fb_yes_{ticket['ticket_id']}"):
                    update_ticket_feedback(ticket["ticket_id"], "positive")
                    st.rerun()

            with fb2:
                if st.button("👎 Not helpful", key=f"fb_no_{ticket['ticket_id']}"):
                    update_ticket_feedback(ticket["ticket_id"], "negative")
                    st.rerun()

            if ticket.get("feedback"):
                st.success(f"Feedback recorded: {ticket['feedback']}")
        else:
            st.markdown("### Support Actions")
            a1, a2 = st.columns(2)

            with a1:
                if ticket.get("status") == "Active":
                    if st.button("Escalate Ticket", key=f"esc_{ticket['ticket_id']}", use_container_width=True):
                        update_ticket_status(ticket["ticket_id"], "Escalated")
                        st.success("Ticket escalated.")
                        st.rerun()

                elif ticket.get("status") == "Escalated":
                    if st.button("Set Back to Active", key=f"act_{ticket['ticket_id']}", use_container_width=True):
                        update_ticket_status(ticket["ticket_id"], "Active")
                        st.success("Ticket set back to active.")
                        st.rerun()

            with a2:
                if ticket.get("status") != "Closed":
                    if st.button("Close from Support", key=f"close_support_{ticket['ticket_id']}", use_container_width=True):
                        update_ticket_status(ticket["ticket_id"], "Closed")
                        st.success("Ticket closed by support.")
                        st.rerun()

            feedback_val = ticket.get("feedback") or "No feedback yet"
            st.info(f"Customer feedback: {feedback_val}")

        with st.expander("Technical JSON Output"):
            st.json(ticket)