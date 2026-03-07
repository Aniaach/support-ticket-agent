import json
from snowflake.snowpark.context import get_active_session


def load_prompt(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()


def extract_json(text):
    """
    Extract the first valid JSON object found in model output.
    """
    text = (text or "").strip()
    decoder = json.JSONDecoder()

    for i, ch in enumerate(text):
        if ch == "{":
            try:
                obj, end = decoder.raw_decode(text[i:])
                return obj
            except json.JSONDecodeError:
                continue

    raise ValueError(f"No valid JSON found in model output: {text}")


def format_retrieved_context(top_k_lines, max_items=5):
    """
    Format retrieved examples into a readable block for the evaluator prompt.
    """
    if not top_k_lines:
        return "No relevant context retrieved."

    formatted_lines = []
    for i, item in enumerate(top_k_lines[:max_items], start=1):
        subject = item.get("SUBJECT", "")
        body = item.get("BODY", "")
        answer = item.get("ANSWER", "")
        similarity = item.get("SIMILARITY", "")

        formatted_lines.append(
            f"""Example {i}:
Subject: {subject}
Body: {body}
Answer: {answer}
Similarity: {similarity}"""
        )

    return "\n\n".join(formatted_lines)


def to_bool(value, default=False):
    """
    Safely convert model outputs to boolean.
    """
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        v = value.strip().lower()
        if v in {"true", "yes", "1"}:
            return True
        if v in {"false", "no", "0"}:
            return False

    if isinstance(value, int):
        return bool(value)

    return default


def derive_action(department_correct, context_relevant, response_relevant, response_coherent):
    """
    Enforce business rules in Python instead of trusting the LLM action.
    """
    if not department_correct:
        return "reroute", False

    if not context_relevant:
        return "escalate", True

    if not response_relevant or not response_coherent:
        return "retry_response", False

    return "approve", False


def compute_quality_score(department_correct, context_relevant, response_relevant, response_coherent):
    """
    Compute a simple quality score between 0 and 1.
    """
    checks = [
        department_correct,
        context_relevant,
        response_relevant,
        response_coherent
    ]
    return round(sum(1 for c in checks if c) / 4.0, 2)


def normalize_reason(reason):
    if reason is None:
        return ""
    return str(reason).strip()


def evaluate_response(ticket_text, department, response, top_k_lines, model="llama3-8b"):
    """
    Evaluate generated response quality and derive final action safely.
    """
    session = get_active_session()

    retrieved_context = format_retrieved_context(top_k_lines)
    prompt_template = load_prompt("prompts/evaluator.txt")

    # Important:
    # the prompt file must escape JSON braces with {{ and }}
    formatted_prompt = prompt_template.format(
        ticket_text=ticket_text,
        department=department,
        retrieved_context=retrieved_context,
        response=response
    )

    query = f"""
        SELECT SNOWFLAKE.CORTEX.COMPLETE(
            '{model}',
            $$ {formatted_prompt} $$
        ) AS evaluation
    """

    result = session.sql(query).collect()
    raw_output = result[0][0]

    parsed = extract_json(str(raw_output))

    department_correct = to_bool(parsed.get("department_correct", False))
    context_relevant = to_bool(parsed.get("context_relevant", False))
    response_relevant = to_bool(parsed.get("response_relevant", False))
    response_coherent = to_bool(parsed.get("response_coherent", False))

    reason = normalize_reason(parsed.get("reason", ""))

    action, human_escalation = derive_action(
        department_correct=department_correct,
        context_relevant=context_relevant,
        response_relevant=response_relevant,
        response_coherent=response_coherent
    )

    quality_score = compute_quality_score(
        department_correct=department_correct,
        context_relevant=context_relevant,
        response_relevant=response_relevant,
        response_coherent=response_coherent
    )

    safe_to_send = action == "approve"

    return {
        "department_correct": department_correct,
        "context_relevant": context_relevant,
        "response_relevant": response_relevant,
        "response_coherent": response_coherent,
        "human_escalation": human_escalation,
        "action": action,
        "reason": reason,
        "quality_score": quality_score,
        "safe_to_send": safe_to_send,
        "raw_model_action": parsed.get("action"),
        "raw_model_human_escalation": parsed.get("human_escalation"),
        "raw_output": str(raw_output)
    }