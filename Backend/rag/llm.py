import os
import requests
from dotenv import load_dotenv
from typing import List

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


import json

def call_llm(prompt: str, model_name: str = "llama3", temperature: float = 0.5, max_tokens: int = 512) -> str:
    """
    Sendet eine Anfrage an einen Ollama-Server (lokal oder remote) und gibt die Antwort zurück.
    """
    #base url with ollama
    url = f"{OLLAMA_BASE_URL}/api/chat"
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "options": {"temperature": temperature, "num_predict": max_tokens},
        "stream": False
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["message"]["content"].strip()
    except Exception as e:
        raise RuntimeError(f"Ollama LLM-Aufruf fehlgeschlagen: {e}")


def ollama_embed(texts, model_name: str = "nomic-embed-text"):
    """
    Holt Embeddings für eine Liste von Texten über Ollama (Embedding-Modell muss geladen sein).
    """
    url = f"{OLLAMA_BASE_URL}/api/embeddings"
    results = []
    for text in texts:
        payload = {"model": model_name, "prompt": text}
        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            results.append(data["embedding"])
        except Exception as e:
            raise RuntimeError(f"Ollama Embedding-Aufruf fehlgeschlagen: {e}")
    return results


def check_ollama_connection() -> bool:
    """
    Prüft ob eine Verbindung zu Ollama hergestellt werden kann.

    Returns:
        bool: True wenn Ollama erreichbar ist, False sonst
    """
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False


def get_available_models() -> List[str]:
    """
    Holt eine Liste der verfügbaren Modelle von Ollama.

    Returns:
        List[str]: Liste der verfügbaren Modell-Namen

    Raises:
        RuntimeError: Bei Fehlern in der Kommunikation mit Ollama
    """
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=10)
        response.raise_for_status()
        data = response.json()

        if "models" not in data:
            return []

        return [model["name"] for model in data["models"]]

    except Exception as e:
        raise RuntimeError(f"Konnte verfügbare Modelle nicht abrufen: {e}")


def test_model_availability(model_name: str) -> bool:
    """
    Testet ob ein spezifisches Modell verfügbar ist.

    Args:
        model_name: Name des zu testenden Modells

    Returns:
        bool: True wenn Modell verfügbar ist, False sonst
    """
    try:
        available_models = get_available_models()
        return model_name in available_models
    except:
        return False
