import json
from snowflake.snowpark.context import get_active_session

def load_prompt(filename):
    """Charge le contenu du fichier texte."""
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()

def format_retrieved_tickets(retrieval_payload, max_results=5):
    """
    Transforme retrieval_payload["results"] en texte lisible pour le prompt.
    """
    results = (retrieval_payload or {}).get("results", [])[:max_results]

    if not results:
        return "No retrieved similar tickets."

    lines = []
    for i, r in enumerate(results, start=1):
        lines.append(
            f"{i}. "
            f"queue={r.get('queue', '')} | "
            f"relevance={r.get('relevance', '')} | "
            f"subject={r.get('subject', '')} | "
            f"body={r.get('body', '')}"
        )
    return "\n".join(lines)

def detect_department(ticket_text, retrieval_payload, language="unknown"):
    session = get_active_session()

    # 1. Charger le prompt système
    prompt_template = load_prompt("prompts/routing.txt")

    # 2. Formatter les tickets similaires
    retrieved_tickets_text = format_retrieved_tickets(retrieval_payload)

    # 3. Injecter les variables dans le prompt
    formatted_prompt = prompt_template.format(
        ticket_text=ticket_text,
        language=language,
        retrieved_tickets=retrieved_tickets_text
    )

    # 4. Appel Cortex
    query = f"""
        SELECT AI_COMPLETE(
            'llama3.3-70b',
            $$ {formatted_prompt} $$,
            {{
                'temperature': 0,
                'max_tokens': 500
            }},
            {{
                'type': 'json',
                'schema': {{
                    'type': 'object',
                    'properties': {{
                        'label': {{'type': 'string'}},
                        'confidence': {{'type': 'number'}},
                        'needs_clarification': {{'type': 'boolean'}},
                        'clarifying_question': {{'type': 'string'}},
                        'rationale': {{'type': 'string'}}
                    }},
                    'required': [
                        'label',
                        'confidence',
                        'needs_clarification',
                        'clarifying_question',
                        'rationale'
                    ]
                }}
            }}
        )
    """

    result = session.sql(query).collect()
    raw_output = result[0][0]

    # AI_COMPLETE avec response_format renvoie un objet JSON/VARIANT structuré
    if isinstance(raw_output, dict):
        parsed = raw_output
    else:
        parsed = json.loads(str(raw_output))

    return parsed