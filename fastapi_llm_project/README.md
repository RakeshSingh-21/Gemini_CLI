
# FastAPI LLM Project

A simple FastAPI project integrated with an LLM (Google Gemini).

## Setup

1. **Create a Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   - Copy `.env` and add your `GEMINI_API_KEY`.

4. **Run the Application:**
   ```bash
   uvicorn app.main:app --reload
   ```

## API Endpoints

- **GET /**: Health check.
- **POST /ask**: Send a message to the LLM.
  - Payload: `{"message": "Hello, how are you?"}`
  - Response: `{"response": "..."}`
