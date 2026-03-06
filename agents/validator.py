import json
from openai import OpenAI

client = OpenAI()

def evaluate_response(ticket_text, response_text, sentiment):
    """
    Evaluate generated response quality
    """

    system_prompt = open("prompts/evaluator.txt").read()

    user_prompt = f"""
Customer ticket:
{ticket_text}

Detected sentiment:
{sentiment}

Generated response:
{response_text}
"""

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    try:
        result = json.loads(completion.choices[0].message.content)
        return result
    except:
        return {
            "quality_score": 0,
            "safe_to_send": False,
            "issues": ["invalid_json"]
        }