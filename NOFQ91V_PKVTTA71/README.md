# Multi-Agent Support Ticket System

This project implements a controlled multi-agent system to automatically process and resolve support tickets.

## Architecture
The system is based on an orchestrated multi-agent pipeline with:
- analysis agents (sentiment, urgency, routing),
- a conditional RAG module using Snowflake Cortex Search,
- a response generation agent,
- a validator agent for evaluation and safety.

## Repository structure
See /docs/architecture.md for details.

## Technologies
- Snowflake & Cortex Search
- LLM-based agents
- Streamlit for demo and monitoring
