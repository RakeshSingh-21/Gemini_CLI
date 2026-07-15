import requests
import json
import os

LLM_SERVER_URL = "http://127.0.0.1:8080/completion"

def ask_llm(prompt: str) -> str:
    try:
        headers = {"Content-Type": "application/json"}
        data = {"prompt": prompt, "n_predict": 128, "temperature": 0.7}
        response = requests.post(LLM_SERVER_URL, headers=headers, data=json.dumps(data), timeout=60)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        response_json = response.json()
        content = response_json.get("content", "").strip()
        
        return content
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to the local LLM server. Please ensure it is running at {LLM_SERVER_URL}."
    except requests.exceptions.Timeout:
        return "Error: The LLM server timed out. Please try again later."
    except requests.exceptions.RequestException as e:
        return f"Error communicating with LLM server: {e}"
    except json.JSONDecodeError:
        return "Error: Failed to decode JSON response from LLM server."
    except Exception as e:
        return f"An unexpected error occurred: {e}"
