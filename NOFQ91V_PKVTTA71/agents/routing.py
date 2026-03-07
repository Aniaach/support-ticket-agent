import json
import re
from snowflake.snowpark.context import get_active_session

ALLOWED_DEPARTMENTS = {
    "Technical Support",
    "Product Support",
    "Customer Service",
    "IT Support",
    "Billing and Payments",
    "Returns and Exchanges",
    "Service Outages and Maintenance",
    "Sales and Pre-Sales",
    "Human Resources",
    "General Inquiry",
}

def load_prompt(filename):
    """Charge le contenu du fichier texte."""
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()

def extract_json(text):
    """Extrait un JSON propre depuis la réponse du modèle."""
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError(f"Aucun JSON valide trouvé dans la sortie : {text}")
        return json.loads(match.group(0))

def detect_department(ticket_text, correction=None): 
    session = get_active_session()
    prompt_template = load_prompt("prompts/routing.txt")
    formatted_prompt = prompt_template.format(ticket_text=ticket_text)
    # Ajout de correction si l'agent d'évaluation a détecté une erreur
    if correction:
        formatted_prompt += f"""
### CORRECTION FROM EVALUATION AGENT ###

The previous department classification was incorrect.

Reason:
{correction}

Select the correct department for this ticket.
Avoid repeating the previous mistake.
"""

    query = f"""
        SELECT SNOWFLAKE.CORTEX.COMPLETE(
            'llama3-8b',
            $$ {formatted_prompt} $$
        ) AS response
    """

    result = session.sql(query).collect()
    raw_output = result[0][0]

    parsed = extract_json(raw_output)
    department = parsed.get("department")

    if department not in ALLOWED_DEPARTMENTS:
        raise ValueError(f"Département invalide retourné : {department}")

    return department