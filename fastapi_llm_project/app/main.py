from fastapi import FastAPI, HTTPException
from schemas import AskRequest, AskResponse
from services.llm_service import get_llm_response

app = FastAPI(title="FastAPI LLM Integration")

@app.get("/")
async def root():
    return {"message": "FastAPI LLM API is running"}

@app.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest):
    if not request.message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    response_text = await get_llm_response(request.message)
    return AskResponse(response=response_text)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
