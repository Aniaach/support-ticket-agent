import os
from snowflake.snowpark.context import get_active_session

def load_prompt(filename):
    """Charge le contenu du fichier texte."""
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()
        
def determine_priority(ticket_text, analysis_object):
    """
    analysis_object est un dictionnaire, ex: {'sentiment': 'Frustration'}
    """
    session = get_active_session()
    
    # Charger le nouveau template de priorité
    prompt_template = load_prompt('prompts/urgency.txt')

    sentiment = analysis_object["sentiment"]
    
    # Injection des deux variables : le texte ET le sentiment extrait précédemment
    #raw_result = session.sql(query).collect()[0][0].strip()
    formatted_prompt = prompt_template.format(
        ticket_text=ticket_text,
        sentiment=sentiment
    )

    query = f"""
        SELECT SNOWFLAKE.CORTEX.COMPLETE(
            'llama3-8b',
            $$ {formatted_prompt} $$
        )
    """
    result = session.sql(query).collect()
    raw_result = result[0][0].strip()
    
    # Découpage du résultat "HIGH | 0.95"
    if "|" in raw_result:
        parts = raw_result.split("|")
        priority = parts[0].strip()
        try:
            confidence = float(parts[1].strip())
        except ValueError:
            confidence = 0.0
    else:
        priority = raw_result
        confidence = 0.0
        
    return priority, confidence