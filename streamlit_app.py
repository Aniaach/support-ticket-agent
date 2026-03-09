import streamlit as st
import pandas as pd

from styles import apply_styles
from database import (
    get_all_tickets,
    get_selected_ticket,
    get_next_ticket_id,
    insert_ticket,
    insert_monitoring,
    update_ticket_status,
    update_ticket_feedback,
    get_tickets_by_client,
    get_ai_monitoring_stats,
    get_ticket_distribution_by_department,
    get_sentiment_distribution,
    get_retry_distribution,
    get_top_clients
)
from pipeline import run_pipeline_simulation, render_static_completed_pipeline

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="AI Support System", layout="wide")
apply_styles()

# =========================================================
# SESSION STATE INIT
# =========================================================
if "selected_ticket_id" not in st.session_state:
    st.session_state.selected_ticket_id = None

if "role" not in st.session_state:
    st.session_state.role = "Customer"

if "last_evaluation_debug" not in st.session_state:
    st.session_state.last_evaluation_debug = None

if "last_pipeline_result" not in st.session_state:
    st.session_state.last_pipeline_result = None

# =========================================================
# UI HELPERS
# =========================================================
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
def priority_badge(priority):

    p = priority.lower()

    if p == "high":
        cls = "priority-high"
    elif p == "medium":
        cls = "priority-medium"
    else:
        cls = "priority-low"

    return f'<span class="badge {cls}">{priority}</span>'

# =========================================================
# HEADER
# =========================================================
st.title("AI Multi-Agent Support System")
#st.caption("Customer support workflow with simulated multi-agent pipeline")

role = st.radio(
    "Workspace Mode",
    ["Customer", "Support Agent"],
    horizontal=True,
    key="role"
)

st.divider()


# =========================================================
# DEBUG PANEL
# =========================================================
if role == "Support Agent" and st.session_state.last_evaluation_debug is not None:
    with st.expander("Debug - Last Evaluation Agent Output", expanded=True):
        eval_debug = st.session_state.last_evaluation_debug
        st.json(eval_debug)
        st.info(f"Last evaluation action: {eval_debug.get('action', 'N/A')}")
        st.caption(f"Reason: {eval_debug.get('reason', '')}")

# =========================================================
# DASHBOARD
# =========================================================
#tickets = get_all_tickets()
if role == "Customer":
    client_id = st.session_state.get("client_id")
    if client_id:
        tickets = get_tickets_by_client(client_id)
    else:
        tickets = []
else:
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

if role == "Support Agent":

    tab_tickets, tab_monitoring, tab_analytics = st.tabs(
        ["Tickets", "AI Monitoring", "Analytics"]
    )
    tickets_container = tab_tickets
    monitoring_container = tab_monitoring
    analytics_container = tab_analytics
else:

    tickets_container = st.container()
    monitoring_container = None
    analytics_container = None

if role == "Support Agent":
    if monitoring_container:
        with monitoring_container:
            st.divider()
            st.subheader("AI Monitoring Dashboard")
        
            stats = get_ai_monitoring_stats()
        
            if stats:
        
                m1, m2, m3, m4= st.columns(4)
        
                m1.metric(
                    "Total Runs",
                    stats["total_runs"]
                )
        
                m2.metric(
                    "Avg Quality Score",
                    round(stats["avg_quality"], 2)
                )
        
                m3.metric(
                    "Safe Responses",
                    f"{round(stats['safe_rate']*100,1)}%"
                )
        
                m4.metric(
                    "Escalation Rate",
                    f"{round(stats['escalation_rate']*100,1)}%"
                )
                
    if analytics_container:
        with analytics_container:
    
            st.subheader("Ticket Analytics")
            dept_data = get_ticket_distribution_by_department()
        
            if dept_data:
            
                st.subheader("Ticket Distribution by Department")
            
                dept_df = pd.DataFrame(dept_data)
            
                st.bar_chart(
                    dept_df.set_index("department")
                )
        
            sentiment_data = get_sentiment_distribution()
        
            if sentiment_data:
            
                st.subheader("Customer Sentiment")
            
                sentiment_df = pd.DataFrame(sentiment_data)
            
                st.bar_chart(
                    sentiment_df.set_index("sentiment")
                )
        
            retry_data = get_retry_distribution()
        
            if retry_data:
            
                st.subheader("AI Retry Distribution")
            
                retry_df = pd.DataFrame(retry_data)
            
                st.bar_chart(
                    retry_df.set_index("retry_count")
                )
        
            top_clients = get_top_clients()
        
            if top_clients:
            
                st.subheader("Top Clients by Ticket Volume")
            
                client_df = pd.DataFrame(top_clients)
            
                st.dataframe(client_df)

# =========================================================
# MAIN LAYOUT
# =========================================================
with tickets_container:
    left, right = st.columns([1, 2], gap="large")
    
    # =========================================================
    # LEFT PANEL
    # =========================================================
    with left:
        if role == "Customer":
            st.subheader("Create Ticket")
    
            # ticket_text = st.text_area(
            #     "Message",
            #     height=140,
            #     placeholder="Describe your issue..."
            # )
    
            # client_id = st.text_input("Client ID", placeholder="e.g. C12345")
            client_id_input = st.text_input("Client ID", placeholder="Enter your client ID. e.g. C1234")
            #st.session_state.client_id = client_id
            if st.button("Connect", use_container_width=True):
                if client_id_input:
                    st.session_state.client_id = client_id_input
                    st.success(f"Connected as {client_id_input}")
                    # if st.button("Disconnect"):
                    #     st.session_state.client_id = None
                    #     st.rerun()
                    st.rerun()
            
                else:
                    st.warning("Please enter your Client ID.")
            
            ticket_text = st.text_area(
                "Message",
                height=140,
                placeholder="Describe your issue..."
            )
            
            animate_pipeline = st.checkbox("Animate multi-agent pipeline", value=True)
            show_debug = role == "Support Agent"
    
            if st.button("Submit Ticket", use_container_width=True):
                #if not st.session_state.get("client_id"):
                    # st.warning("Please connect with your Client ID before submitting a ticket.")
                    # if ticket_text.strip():
                if not st.session_state.get("client_id"):
                    st.warning("Please connect with your Client ID before submitting a ticket.")
                
                elif not ticket_text.strip():
                    st.warning("Please enter a message before submitting.")
                
                else:
                        with st.spinner("Processing ticket..."):
                            result = run_pipeline_simulation(
                                ticket_text,
                                animate=animate_pipeline,
                                show_debug=show_debug
                            )
        
                        ticket_id = get_next_ticket_id()
        
                        ticket_data = {
                            "ticket_id": ticket_id,
                            "client_id": st.session_state.get("client_id"),
                            "ticket_text": ticket_text.strip(),
                            "sentiment": result["sentiment"],
                            "priority": result["priority"],
                            "confidence": result["confidence"],
                            "department": result["department"],
                            "generated_response": result["response"],
                            "status": result["status"],
                            "feedback": None,
                            "quality_score": result["quality_score"],
                            "safe_to_send": result["safe_to_send"],
                            "retry_count": result["retry_count"]
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
        if role == "Customer" and not st.session_state.get("client_id"):
            st.info("Enter your Client ID to see your tickets.")
        st.subheader("Ticket History")
    
        filtered_tickets = []
    
        if role == "Customer":
            customer_search = st.text_input("Search my tickets")
            #customer_client_filter = st.text_input("Filter by my Client ID")
    
            for t in tickets:
                if customer_search and customer_search.lower() not in str(t.get("ticket_text", "")).lower():
                    continue
    
                # if customer_client_filter and customer_client_filter.lower() not in str(t.get("client_id", "")).lower():
                #     continue
    
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
    
        # if not filtered_tickets:
        #     st.caption("No matching tickets.")
        # else:
        #     for t in filtered_tickets:
        #         tid = t.get("ticket_id", "?")
        #         prio = t.get("priority", "N/A")
        #         status = t.get("status", "N/A")
        #         ts = str(t.get("created_at", ""))[:16]
        #         icon = priority_icon(prio)
    
        #         label = f"#{tid} {icon} {prio} • {status}"
        #         if ts and ts != "None":
        #             label += f" • {ts}"
    
        #         if st.button(label, key=f"hist_{tid}", use_container_width=True):
        #             st.session_state.selected_ticket_id = tid
        if not filtered_tickets:
            st.caption("No matching tickets.")
        else:
        
            st.markdown('<div class="ticket-list">', unsafe_allow_html=True)

            for t in filtered_tickets:
            
                tid = t.get("ticket_id", "?")
                prio = t.get("priority", "N/A")
                status = t.get("status", "N/A")
                dept = t.get("department", "N/A")
                ts = str(t.get("created_at", ""))[:16]
                text = str(t.get("ticket_text", "") or "")
                
                preview = text[:60].strip()
                if len(text) > 60:
                    preview += "..."
                
                icon = priority_icon(prio)
               
                label= f"#{tid} {icon} {prio} • {status} • {dept} • {ts} — {preview}"
                
                if st.button(label, key=f"hist_{tid}", use_container_width=True):
                    st.session_state.selected_ticket_id = tid
    
    # =========================================================
    # RIGHT PANEL
    # =========================================================
    with right:
        ticket = get_selected_ticket(st.session_state.get("selected_ticket_id"))
    
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
                    #f'{priority_badge(ticket.get("priority"))}',
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
                '<div class="muted">This ticket went through the full agent workflow: Sentiment → Priority → Routing → RAG → Response → Evaluation.</div>',
                unsafe_allow_html=True
            )
    
            if role == "Support Agent":
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
    
            # st.markdown("### Knowledge Context Used")
            # st.caption("Context lines are used during generation but are not stored in support_tickets.")
    
            if st.session_state.last_pipeline_result is not None:
                with st.expander("Pipeline Debug Result", expanded=False):
                    st.json(st.session_state.last_pipeline_result)
    
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
                technical_output = dict(ticket)
                technical_output["correction"] = ticket.get("correction")
                st.json(technical_output)