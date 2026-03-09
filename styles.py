import streamlit as st

CUSTOM_CSS = """
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

.priority-high {
    background:#FEE2E2;
    color:#991B1B;
}

.priority-medium {
    background:#FEF3C7;
    color:#92400E;
}

.priority-low {
    background:#DCFCE7;
    color:#166534;
}
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

/* Debug box */
.debug-box {
    border:1px solid #BFDBFE;
    background:#EFF6FF;
    border-radius:12px;
    padding:12px;
}

</style>
"""

def apply_styles():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)