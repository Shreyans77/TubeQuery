from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from . import rag_engine

app = FastAPI()

# Enable CORS (useful if serving frontend separately, though we serve static here)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global storage for the current session's RAG components
# In a real app, this would be a cache or database keyed by session ID
current_rag = {
    "retriever": None,
    "model": None,
    "prompt": None
}

class URLRequest(BaseModel):
    url: str

class ChatRequest(BaseModel):
    question: str

@app.post("/api/process")
async def process_video(request: URLRequest):
    try:
        retriever, model, prompt = rag_engine.get_rag_chain(request.url)
        current_rag["retriever"] = retriever
        current_rag["model"] = model
        current_rag["prompt"] = prompt
        return {"status": "success", "message": "Video processed successfully!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/chat")
async def chat(request: ChatRequest):
    if not current_rag["retriever"]:
        raise HTTPException(status_code=400, detail="No video processed yet. Please process a video first.")
    
    try:
        answer = rag_engine.answer_question(
            current_rag["retriever"],
            current_rag["model"],
            current_rag["prompt"],
            request.question
        )
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files to serve the frontend
# Must be last to avoid overriding API routes
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
