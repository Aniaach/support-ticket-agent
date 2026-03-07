import json
from snowflake.snowpark.context import get_active_session

#from Preprocessing import clean_text, create_embedding, search_top5
from agents.Preprocessing import clean_text, create_embedding, search_top5

# Naila — Charge le prompt depuis un fichier texte
def load_prompt(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()


# Naila — Extrait le premier objet JSON valide même si le modèle ajoute du texte avant/après
def extract_json(text):
    text = (text or "").strip()
    decoder = json.JSONDecoder()

    for i, ch in enumerate(text):
        if ch == "{":
            try:
                obj, end = decoder.raw_decode(text[i:])
                return obj
            except json.JSONDecodeError:
                continue

    raise ValueError(f"Aucun JSON valide trouvé dans la sortie : {text}")


# Naila — Transforme les 5 tickets récupérés en texte lisible pour le prompt
def format_retrieved_context(top_k_lines, max_items=5):
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


# Naila — Génère la réponse client à partir du ticket, département, sentiment et contexte RAG
def generate_response(ticket_text, department, sentiment, model="llama3-8b"):
    session = get_active_session()

    # 1) Nettoyage du ticket
    cleaned_ticket = clean_text(ticket_text)

    # 2) Génération embedding
    embedding = create_embedding(session, cleaned_ticket)

    # 3) Recherche du vrai top 5
    top_k_lines = search_top5(session, embedding, department)

    # 4) Formatage du contexte RAG
    retrieved_context = format_retrieved_context(top_k_lines)

    # 5) Chargement et remplissage du prompt
    prompt_template = load_prompt("prompts/response.txt")
    formatted_prompt = prompt_template.format(
        ticket_text=ticket_text,
        department=department,
        sentiment=sentiment,
        retrieved_context=retrieved_context
    )

    query = f"""
        SELECT SNOWFLAKE.CORTEX.COMPLETE(
            '{model}',
            $$ {formatted_prompt} $$
        ) AS response
    """

    result = session.sql(query).collect()
    raw_output = result[0][0]

    print("RAW RESPONSE OUTPUT:", raw_output)
    print("TOP 5 RETRIEVED:", top_k_lines)

    parsed = extract_json(str(raw_output))
    return parsed.get("response", "").strip()