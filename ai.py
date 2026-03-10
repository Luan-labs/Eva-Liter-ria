# ai.py
import os
import requests

# Pega a chave da variável de ambiente
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

def perguntar(prompt):
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    data = {
        "model": "claude-3-haiku-20240307",
        "max_tokens": 800,
        "messages": [
            {"role": "user", "content": [{"type": "text", "text": prompt}]}
        ]
    }
    r = requests.post(url, headers=headers, json=data)
    if r.status_code != 200:
        return "Erro na IA"
    return r.json()["content"][0]["text"]
