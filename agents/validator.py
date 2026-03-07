import json
from snowflake.snowpark.context import get_active_session


def load_prompt(filename):
    """Load prompt template from file."""
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()


def validate_response(ticket_text, response, sentiment):
    """
    Validate the generated response using Snowflake Cortex.

    Returns:
    {
        "quality_score": float,
        "safe_to_send": bool,
        "issues": list
    }
    """

    session = get_active_session()

    # Load prompt template
    prompt_template = load_prompt("prompts/evaluator.txt")

    # Inject variables into prompt
    formatted_prompt = prompt_template.format(
        ticket_text=ticket_text,
        sentiment=sentiment,
        response=response
    )

    query = f"""
        SELECT SNOWFLAKE.CORTEX.COMPLETE(
            'llama3-8b',
            $$ {formatted_prompt} $$
        )
    """

    try:
        result = session.sql(query).collect()
        raw_output = result[0][0].strip()

        # Attempt JSON parsing
        parsed = json.loads(raw_output)

        quality_score = float(parsed.get("quality_score", 0))
        safe_to_send = bool(parsed.get("safe_to_send", False))
        issues = parsed.get("issues", [])

        return {
            "quality_score": quality_score,
            "safe_to_send": safe_to_send,
            "issues": issues
        }

    except Exception as e:
        # Fallback if LLM output isn't valid JSON
        return {
            "quality_score": 0.0,
            "safe_to_send": False,
            "issues": [f"validator_error: {str(e)}"]
        }