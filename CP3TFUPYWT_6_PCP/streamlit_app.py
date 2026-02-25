import streamlit as st
from datetime import datetime
from agents.analyse_sentiment import detect_sentiment
# Import de ton nouvel agent
from agents.analyse_priorite import determine_priority 

# =========================================================
# CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="Support Ticket Agent",
    page_icon="🎫",
    layout="wide"
)

# =========================================================
# AGENT ORCHESTRATION
# =========================================================

def analyze_ticket(raw_text):
    """
    Orchestre les agents d'analyse : Sentiment puis Priorité
    """
    # 1. Extraction du sentiment
    sentiment = detect_sentiment(raw_text)
    
    # 2. Création de l'objet intermédiaire pour l'agent de priorité
    analysis_obj = {"sentiment": sentiment}
    
    # 3. Calcul de la priorité en utilisant le texte ET le sentiment
    priority_result = determine_priority(raw_text, analysis_obj)

    
    return {
        "sentiment": sentiment,
        "priority": priority_result[0], 
        "confidence" :  priority_result[1], 
        "department": "IT Support" # Placeholder pour le routing
    }

# ... (garder les fonctions retrieve_knowledge, generate_response, etc. telles quelles)

# =========================================================
# INITIALISATION SESSION
# =========================================================
if "ticket_state" not in st.session_state:
    st.session_state.ticket_state = None

# =========================================================
# HEADER
# =========================================================
st.title("🎫 Multi-Agent Support Ticket System")
st.caption("Pipeline: Sentiment Analysis -> Priority Scoring -> Routing")
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
    with st.spinner("Agents are analyzing your ticket..."):
        # On lance l'analyse complète
        analysis = analyze_ticket(ticket_text)

        st.session_state.ticket_state = {
            "raw_text": ticket_text,
            "analysis": analysis,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

# =========================================================
# SECTION 2 - DISPLAY RESULTS
# =========================================================
if st.session_state.ticket_state:
    state = st.session_state.ticket_state
    analysis = state["analysis"]

    st.subheader("2️⃣ Analysis Results")
    
    # Affichage plus visuel sous forme de colonnes/badges
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        st.metric("Detected Sentiment", analysis["sentiment"])
    
    with col_b:
        # Couleur dynamique pour la priorité
        color = "red" 
        st.markdown(f"**Priority:** :{color}[{analysis['priority']}]")
        
    with col_c:
        st.info(f"Department: {analysis['department']}")

    with st.expander("View Raw JSON Data"):
        st.json(state)

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("👍 Helpful"):
            st.success("Feedback recorded.")
    with col2:
        if st.button("👎 Not Helpful"):
            st.error("Feedback recorded.")