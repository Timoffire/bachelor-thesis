import os
import requests
from dotenv import load_dotenv
from typing import List
import logging

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

def call_llm(prompt: str, model_name: str = "llama3", temperature: float = 0.01, max_tokens: int = 512) -> str:
    """
    sends a prompt to the specified Ollama model and returns the response text.
    Args:
        prompt: The input text prompt to send to the model.
        model_name: The name of the Ollama model to use (default: "llama3").
        temperature: Sampling temperature for response generation (default: 0.01).
        max_tokens: Maximum number of tokens to generate in the response (default: 512).
    Returns:
        The generated response text from the model.
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
        logging.info("Request sent to Ollama")
        response.raise_for_status()
        data = response.json()
        return data["message"]["content"].strip()
    except Exception as e:
        raise RuntimeError(f"Ollama LLM-Aufruf fehlgeschlagen: {e}")


def ollama_embed(texts, model_name: str = "nomic-embed-text"):
    """
    Calls the Ollama embedding endpoint for a list of texts.
    Args:
        texts: List of text strings to embed.
        model_name: The name of the embedding model to use (default: "nomic-embed-text").
    Returns:
        List of embeddings corresponding to the input texts.
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
    Checks if the Ollama server is reachable.
    Returns:
        bool: True if the server is reachable, False otherwise
    """
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False


def get_available_models() -> List[str]:
    """
    gets a list of available models from the Ollama server.
    Returns:
        List[str]: List of model names
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
    tests if a specific model is available on the Ollama server.
    Args:
        model_name: The name of the model to check.
    Returns:
        bool: True if the model is available, False otherwise.
    """
    try:
        available_models = get_available_models()
        return model_name in available_models
    except:
        return False
