# ai.py
import os
import requests

# Pega a chave da variável de ambiente
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

def perguntar(prompt):
    """Função que envia um prompt à API Claude"""
    
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
            {"role": "user", "content": prompt}
        ]
    }

    r = requests.post(url, headers=headers, json=data)

    if r.status_code != 200:
        return f"Erro na IA: {r.text}"

    return r.json()["content"][0]["text"]


# =========================
# FUNÇÕES DE ENGENHARIA DE TEXTO
# =========================

def resumir(texto):
    prompt = f"Resuma o texto abaixo em uma versão curta mantendo as ideias principais:\n\n{texto}"
    return perguntar(prompt)


def analisar_estilo(texto):
    prompt = f"Analise o estilo literário do texto abaixo e sugira melhorias:\n\n{texto}"
    return perguntar(prompt)


def gerar_sugestoes(texto):
    prompt = f"Para o texto abaixo, sugira 3 melhorias criativas ou alternativas de desenvolvimento:\n\n{texto}"
    return perguntar(prompt)
