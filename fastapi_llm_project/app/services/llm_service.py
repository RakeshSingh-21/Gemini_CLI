import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model_name = os.getenv("LLM_MODEL", "gemini-2.5-flash")
model = genai.GenerativeModel(model_name)

async def get_llm_response(message: str) -> str:
    try:
        response = model.generate_content(message)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"
