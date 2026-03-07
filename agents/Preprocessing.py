import re

import re
import snowflake.connector
import json


def clean_text(raw_text: str) -> str:
    text = raw_text.lower()

    text = re.sub(r"(^|\n)\s*(dear\s+(sir|madam|customer|team|support)|hello|hi there|hi|hey|good morning|good afternoon|good evening|hallo|guten\s+(tag|morgen|abend)|sehr\s+geehrte[r]?\s*(damen\s+und\s+herren|herr|frau)?|liebe[r]?\s*(kunde|kundin)?)[,\s]*", " ", text, flags=re.I)

    text = re.sub(r"(best\s+regards|kind\s+regards|regards|sincerely|yours\s+(truly|faithfully)|thank\s+you|thanks|cheers|mit\s+freundlichen\s+gr[üu]ßen|freundliche\s+gr[üu]ße|mfg|vielen\s+dank|danke\s*(sch[oö]n|sehr)?|hochachtungsvoll)[,\s]*", " ", text, flags=re.I)

    text = re.sub(r"(sent\s+from\s+my\s+(iphone|android|mobile)|--+\s*original\s+message|---+)", " ", text, flags=re.I)

    text = re.sub(r"<[^>]+>", " ", text)

    text = re.sub(r"https?://[^\s]+|www\.[^\s]+", " ", text)

    text = re.sub(r"\s{2,}", " ", text)

    return text.strip()


import snowflake.connector
import json

import numpy as np
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col, lit

def create_embedding(session: Session, text: str):
    """
    Génère un embedding pour un texte donné en utilisant la fonction EMBED_TEXT_1024.
    Retourne un vecteur de type list[float].
    """
    query = f"""
    SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_1024(
        'snowflake-arctic-embed-l-v2.0',
        '{text.replace("'", "''")}'
    ) AS embedding
    """
    result = session.sql(query).collect()
    embedding_vector = result[0]['EMBEDDING']  # C'est un VECTOR
    # Convertir en liste Python
    return list(embedding_vector)

def search_top5(session: Session, embedding: list, department: str):
    """
    Recherche les 5 tickets les plus similaires dans la file 'department' 
    en utilisant le vecteur embedding fourni.
    """
    # Récupérer tous les tickets de la file
    df = (
        session.table("PROJET_TAL.PUBLIC.TICKETS_EMBEDDED")
        .filter(col("QUEUE") == lit(department))
        .select("SUBJECT", "BODY", "ANSWER", "QUEUE", "EMBEDDING")
    )

    # Collecter tous les tickets côté Python
    tickets = df.collect()

    results = []
    emb_np = np.array(embedding, dtype=float)

    for row in tickets:
        ticket_emb = np.array(row['EMBEDDING'], dtype=float)
        # Calcul de la similarité cosine
        sim = float(np.dot(emb_np, ticket_emb) / (np.linalg.norm(emb_np) * np.linalg.norm(ticket_emb)))
        results.append({
            "SUBJECT": row["SUBJECT"],
            "BODY": row["BODY"],
            "ANSWER": row["ANSWER"],
            "QUEUE": row["QUEUE"],
            "SIMILARITY": sim
        })

    # Trier par similarité décroissante et retourner top 5
    top5 = sorted(results, key=lambda x: x["SIMILARITY"], reverse=True)[:5]
    return top5
    
