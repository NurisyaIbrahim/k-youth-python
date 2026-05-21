# prompt_model.py
import sys
import os
import requests
from google import genai
from google.genai import types

# Ollama endpoint
OLLAMA_URL = "http://localhost:11434/api/generate"

# --- Helper Functions ---
def prompt_ollama(model: str, prompt: str) -> str:
    """Call Ollama local model."""
    try:
        payload = {"model": model, "prompt": prompt, "stream": False}
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "No response from Ollama")
    except requests.exceptions.ConnectionError:
        return "[Ollama Error] Ollama is not running. Please start Ollama."
    except Exception as e:
        return f"[Ollama Error] {str(e)}"

def prompt_gemini(model: str, prompt: str) -> str:
    """Call Google Gemini API using the new google.genai SDK."""
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return "[Gemini Error] No API key found. Set GOOGLE_API_KEY environment variable."

    try:
        # Create a client with API key
        client = genai.Client(api_key=api_key)

        # Generate content using the new SDK's syntax
        response = client.models.generate_content(
            model=model,
            contents=prompt
        )
        return response.text
    except Exception as e:
        error_msg = str(e)
        if "503" in error_msg:
            return "[Gemini Error] 503 UNAVAILABLE. Model is busy. Please try again later."
        if "429" in error_msg:
            return "[Gemini Error] 429 Rate limit exceeded."
        return f"[Gemini Error] {error_msg}"

def prompt_model(model: str, prompt: str) -> str:
    """Route to the correct model handler."""
    ollama_models = ["llama3.1", "phi3", "deepseek-r1:1.5b"]
    if model in ollama_models:
        return prompt_ollama(model, prompt)
    # All other model names are assumed to be Gemini models
    return prompt_gemini(model, prompt)

def main():
    if len(sys.argv) < 3:
        print("Usage: uv run prompt_model.py <model> <prompt>")
        print("\nOllama models: llama3.1, phi3, deepseek-r1:1.5b")
        print("Gemini models: gemini-2.5-flash, gemini-2.5-flash-lite, gemini-3-flash-preview")
        print('\nExample:')
        print('  uv run prompt_model.py llama3.1 "Tell me a joke"')
        return

    model = sys.argv[1]
    prompt = sys.argv[2]

    print("\n--- RESPONSE ---")
    response = prompt_model(model, prompt)
    print(response)

if __name__ == "__main__":
    main()