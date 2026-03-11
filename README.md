# Multi-Agent Support Ticket System

AI-powered support ticket automation using RAG and multi-agent LLM architecture.

---

This project implements an intelligent **multi-agent system for automated customer support ticket processing**.

The system uses a **RAG (Retrieval-Augmented Generation) architecture** combined with multiple LLM agents to analyze, classify, route, and respond to customer tickets.

The application includes a **Streamlit interface**, **AI monitoring dashboard**, and **analytics tools** built on top of **Snowflake**.

---

# System Architecture

The system is based on a **multi-agent pipeline** where each agent performs a specialized task.

### Pipeline workflow

1. **Preprocessing Agent**
   - Cleans the ticket text
   - Removes signatures, greetings, URLs, and noise

2. **Sentiment Agent**
   - Detects the emotional tone of the message
   - Categories include frustration, stress, confusion, neutral, etc.

3. **Priority Agent**
   - Estimates ticket urgency (LOW / MEDIUM / HIGH)
   - Uses ticket context and sentiment

4. **Routing Agent**
   - Assigns the ticket to the correct department
   - (IT Support, Billing, HR, Sales, etc.)

5. **RAG Agent**
   - Generates embeddings
   - Retrieves the most relevant historical tickets using **Snowflake Cortex Search**

6. **Response Agent**
   - Generates a professional response using the ticket and retrieved context

7. **Evaluation Agent**
   - Validates response relevance and safety
   - May trigger retry or human escalation

---

# Streamlit Application

The project includes an interactive **Streamlit interface** with two user modes.

### Customer Mode

Users can:
- connect using a client ID
- submit a support ticket
- view generated responses
- provide feedback on responses

### Support Agent Mode

Support agents can:
- browse and search tickets
- close, reopen, or escalate tickets
- inspect ticket analysis results
- access monitoring dashboards

---

# Monitoring & Analytics

The system includes built-in **AI monitoring and analytics dashboards**.

### AI Monitoring

Tracks the performance of the multi-agent system:

- total pipeline runs
- average response quality score
- safe response rate
- escalation rate
- retry distribution

### Ticket Analytics

Provides insights into support activity:

- ticket distribution by department
- customer sentiment distribution
- retry distribution
- top clients by ticket volume

---

# Technologies

- Snowflake
- Snowflake Cortex (LLM + embeddings)
- Python
- Streamlit
- Retrieval-Augmented Generation (RAG)
- Multi-agent LLM architecture

---

# Authors

- Ania Chikh  
- Celina Bedjou  
- Naila Boudedja  
- Taous Habbak  

Master ISD – Université Paris-Saclay  
2025–2026
