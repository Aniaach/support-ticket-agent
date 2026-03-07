import time
import streamlit as st

from snowflake.snowpark.context import get_active_session

from agents.analyse_sentiment import detect_sentiment
from agents.analyse_priorite import determine_priority
from agents.routing import detect_department
from agents.response import generate_response
from agents.Preprocessing import clean_text, create_embedding, search_top5
from agents.evaluate_response import evaluate_response

session = get_active_session()

PIPELINE_STEPS = [
    "Ticket",
    "Sentiment Agent",
    "Priority Agent",
    "Routing Agent",
    "RAG Agent",
    "Response Agent",
    "Evaluation Agent"
]

MAX_RETRIES = 2
DEFAULT_DEPARTMENT = "General Inquiry"


def render_pipeline(active_index=-1, completed_until=-1, container=None):
    html = '<div class="pipeline-wrap">'
    for i, step in enumerate(PIPELINE_STEPS):
        cls = "pipeline-step"
        if i <= completed_until:
            cls += " done"
        elif i == active_index:
            cls += " active"

        html += f'<div class="{cls}">{step}</div>'
        if i < len(PIPELINE_STEPS) - 1:
            html += '<div class="pipeline-arrow">→</div>'
    html += "</div>"

    if container is not None:
        container.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown(html, unsafe_allow_html=True)


def render_static_completed_pipeline():
    render_pipeline(active_index=-1, completed_until=len(PIPELINE_STEPS) - 1)


def display_agent_log(message, container):
    container.markdown(f'<div class="agent-log">{message}</div>', unsafe_allow_html=True)


def safe_evaluation_fallback(reason):
    return {
        "department_correct": False,
        "context_relevant": False,
        "response_relevant": False,
        "response_coherent": False,
        "human_escalation": True,
        "action": "escalate",
        "reason": reason,
        "quality_score": 0.0,
        "safe_to_send": False,
        "raw_model_action": None,
        "raw_model_human_escalation": None
    }


def maybe_sleep(animate, seconds):
    if animate:
        time.sleep(seconds)


def run_pipeline_simulation(raw_text, animate=True, show_debug=True):
    pipeline_placeholder = st.empty()
    log_placeholder = st.empty()
    debug_placeholder = st.empty()
    error_placeholder = st.empty()

    retry_count = 0
    correction = None
    action = None
    evaluation = {}
    response = ""
    top5_context = []

    sentiment = "Neutral"
    priority = "Low"
    confidence = 0.0
    department = DEFAULT_DEPARTMENT

    render_pipeline(active_index=0, completed_until=-1, container=pipeline_placeholder)
    display_agent_log("🎫 Ticket received.", log_placeholder)
    maybe_sleep(animate, 0.35)

    render_pipeline(active_index=1, completed_until=0, container=pipeline_placeholder)
    display_agent_log("😊 Sentiment Agent analysing ticket tone...", log_placeholder)

    try:
        sentiment = detect_sentiment(raw_text)
        print("[Sentiment]", sentiment)
    except Exception as e:
        print("[SENTIMENT ERROR]", e)
        sentiment = "Neutral"
        if show_debug:
            error_placeholder.error(f"SENTIMENT ERROR: {type(e).__name__} - {e}")

    maybe_sleep(animate, 0.45)

    render_pipeline(active_index=2, completed_until=1, container=pipeline_placeholder)
    display_agent_log("⚡ Priority Agent calculating urgency level...", log_placeholder)

    try:
        priority, confidence = determine_priority(raw_text, {"sentiment": sentiment})
        print("[Priority]", priority, "| confidence =", confidence)
    except Exception as e:
        print("[PRIORITY ERROR]", e)
        priority, confidence = "Low", 0.0
        if show_debug:
            error_placeholder.error(f"PRIORITY ERROR: {type(e).__name__} - {e}")

    maybe_sleep(animate, 0.45)

    render_pipeline(active_index=3, completed_until=2, container=pipeline_placeholder)
    display_agent_log("🧭 Routing Agent identifying target department...", log_placeholder)

    try:
        department = detect_department(raw_text)
        print("[Routing] department =", department)
    except Exception as e:
        print("[Routing ERROR]", e)
        department = DEFAULT_DEPARTMENT
        if show_debug:
            error_placeholder.error(f"ROUTING ERROR: {type(e).__name__} - {e}")

    maybe_sleep(animate, 0.45)

    render_pipeline(active_index=4, completed_until=3, container=pipeline_placeholder)
    display_agent_log("📚 RAG Agent retrieving the most relevant context...", log_placeholder)

    try:
        cleaned_ticket = clean_text(raw_text)
        embedding = create_embedding(session, cleaned_ticket)
        top5_context = search_top5(session, embedding, department)
        print("[RAG] top5_context count =", len(top5_context))
    except Exception as e:
        print("[RAG ERROR]", e)
        top5_context = []
        if show_debug:
            error_placeholder.error(f"RAG ERROR: {type(e).__name__} - {e}")

    maybe_sleep(animate, 0.45)

    while True:
        if retry_count > MAX_RETRIES:
            print("[Loop] Max retries exceeded -> escalate")
            action = "escalate"
            evaluation = safe_evaluation_fallback("Maximum retry count exceeded.")
            correction = evaluation["reason"]
            st.session_state.last_evaluation_debug = {
                "stage": "retry_limit",
                "evaluation": evaluation
            }
            break

        render_pipeline(active_index=5, completed_until=4, container=pipeline_placeholder)
        display_agent_log("✍️ Response Agent generating a draft answer...", log_placeholder)

        try:
            response = generate_response(
                ticket_text=raw_text,
                department=department,
                sentiment=sentiment,
                top_k_lines=top5_context,
                correction=correction
            )
            print("[Response] generated successfully")
            print("[Response text]", response)
        except Exception as e:
            print("[RESPONSE ERROR]", e)
            response = "We have received your request and our support team will review it shortly."
            action = "escalate"
            evaluation = safe_evaluation_fallback(f"Response generation failed: {str(e)}")
            correction = evaluation["reason"]

            st.session_state.last_evaluation_debug = {
                "stage": "response_generation",
                "error_type": type(e).__name__,
                "error_message": str(e),
                "evaluation": evaluation
            }

            if show_debug:
                error_placeholder.error(f"RESPONSE ERROR: {type(e).__name__} - {e}")
                debug_placeholder.markdown("### Debug - Response Error")
                debug_placeholder.json(st.session_state.last_evaluation_debug)

            break

        maybe_sleep(animate, 0.45)

        render_pipeline(active_index=6, completed_until=5, container=pipeline_placeholder)
        display_agent_log("🧠 Evaluation Agent verifying response quality...", log_placeholder)

        try:
            evaluation = evaluate_response(
                ticket_text=raw_text,
                department=department,
                response=response,
                top_k_lines=top5_context
            )
            print("[Evaluation]", evaluation)

            st.session_state.last_evaluation_debug = {
                "stage": "evaluate_response_success",
                "evaluation": evaluation
            }

            if show_debug:
                debug_placeholder.markdown("### Debug - Evaluation Agent Output")
                debug_placeholder.json(evaluation)

        except Exception as e:
            print("[EVALUATION ERROR]", e)
            action = "escalate"
            evaluation = safe_evaluation_fallback(f"Evaluation agent failed: {str(e)}")
            correction = evaluation["reason"]

            st.session_state.last_evaluation_debug = {
                "stage": "evaluate_response_exception",
                "error_type": type(e).__name__,
                "error_message": str(e),
                "ticket_text": raw_text,
                "department": department,
                "response_preview": response[:1000] if response else "",
                "top5_context_count": len(top5_context) if top5_context else 0,
                "evaluation_fallback": evaluation
            }

            if show_debug:
                error_placeholder.error(f"EVALUATION ERROR: {type(e).__name__} - {e}")
                debug_placeholder.markdown("### Debug - Evaluation Error Details")
                debug_placeholder.json(st.session_state.last_evaluation_debug)

            break

        action = evaluation.get("action", "escalate")
        correction = evaluation.get("reason", "")
        print("[Decision] action =", action)
        print("[Decision] correction =", correction)

        if show_debug:
            st.session_state.last_evaluation_debug["decision"] = {
                "action": action,
                "correction": correction
            }

        if action == "approve":
            break

        if action == "reroute":
            retry_count += 1

            display_agent_log(
                f"🔁 Evaluation detected wrong department. Re-running Routing Agent... (retry {retry_count}/{MAX_RETRIES})",
                log_placeholder
            )

            try:
                try:
                    department = detect_department(raw_text, correction=correction)
                except TypeError:
                    department = detect_department(raw_text)

                print("[Reroute] new department =", department)
            except Exception as e:
                print("[REROUTE ERROR]", e)
                action = "escalate"
                evaluation = safe_evaluation_fallback(f"Routing retry failed: {str(e)}")
                correction = evaluation["reason"]

                st.session_state.last_evaluation_debug = {
                    "stage": "reroute_exception",
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "evaluation_fallback": evaluation
                }

                if show_debug:
                    error_placeholder.error(f"REROUTE ERROR: {type(e).__name__} - {e}")
                    debug_placeholder.markdown("### Debug - Reroute Error")
                    debug_placeholder.json(st.session_state.last_evaluation_debug)

                break

            try:
                cleaned_ticket = clean_text(raw_text)
                embedding = create_embedding(session, cleaned_ticket)
                top5_context = search_top5(session, embedding, department)
                print("[RAG after reroute] top5_context count =", len(top5_context))
            except Exception as e:
                print("[RAG AFTER REROUTE ERROR]", e)
                action = "escalate"
                evaluation = safe_evaluation_fallback(f"RAG retrieval after reroute failed: {str(e)}")
                correction = evaluation["reason"]

                st.session_state.last_evaluation_debug = {
                    "stage": "rag_after_reroute_exception",
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "evaluation_fallback": evaluation
                }

                if show_debug:
                    error_placeholder.error(f"RAG AFTER REROUTE ERROR: {type(e).__name__} - {e}")
                    debug_placeholder.markdown("### Debug - RAG After Reroute Error")
                    debug_placeholder.json(st.session_state.last_evaluation_debug)

                break

            continue

        if action == "retry_response":
            retry_count += 1
            display_agent_log(
                f"🔁 Evaluation requested response regeneration... (retry {retry_count}/{MAX_RETRIES})",
                log_placeholder
            )
            continue

        if action == "escalate":
            display_agent_log(
                "⚠️ Context retrieval failed or answer not safe enough. Escalating to human support.",
                log_placeholder
            )
            break

        print("[Unknown action] forcing escalate")
        action = "escalate"
        evaluation = safe_evaluation_fallback("Unknown evaluation action returned.")
        correction = evaluation["reason"]

        st.session_state.last_evaluation_debug = {
            "stage": "unknown_action",
            "received_action": action,
            "evaluation_fallback": evaluation
        }

        if show_debug:
            debug_placeholder.markdown("### Debug - Unknown Action")
            debug_placeholder.json(st.session_state.last_evaluation_debug)

        break

    render_pipeline(active_index=-1, completed_until=len(PIPELINE_STEPS) - 1, container=pipeline_placeholder)
    display_agent_log("✅ Multi-agent workflow completed.", log_placeholder)

    final_human_escalation = evaluation.get("human_escalation", False) if evaluation else False
    status = "Escalated" if action == "escalate" or final_human_escalation else "Active"

    result = {
        "sentiment": sentiment,
        "priority": priority,
        "confidence": float(confidence) if confidence is not None else 0.0,
        "status": status,
        "department": department,
        "response": response,
        "top5_context": top5_context,
        "feedback": None,
        "retry_count": retry_count,
        "evaluation": evaluation,
        "correction": correction,
        "quality_score": evaluation.get("quality_score", 0.0) if evaluation else 0.0,
        "safe_to_send": evaluation.get("safe_to_send", False) if evaluation else False,
        "last_pipeline_steps": PIPELINE_STEPS
    }

    st.session_state.last_pipeline_result = result
    return result