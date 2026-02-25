import os
from snowflake.snowpark.context import get_active_session

def load_prompt(filename):
    """Charge le contenu du fichier texte."""
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()

def detect_sentiment(ticket_text):
    session = get_active_session()
    
    # 1. Importation du prompt depuis le fichier externe
    prompt_template = load_prompt('prompts/sentiment.txt')

    # 2. Injection de la variable
    formatted_prompt = prompt_template.format(ticket_text=ticket_text)

    # 3. Exécution de la requête Cortex
    query = f"""
        SELECT SNOWFLAKE.CORTEX.COMPLETE(
            'llama3-8b',
            $$ {formatted_prompt} $$
        )
    """

    result = session.sql(query).collect()
    return result[0][0].strip()