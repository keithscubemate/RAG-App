from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
from google import genai
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

frontend_path = os.path.join(os.path.dirname(__file__), "rag_frontend", "build")

app.mount("/static", StaticFiles(directory=os.path.join(frontend_path, "static")))

origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:8000",
    "http://192.168.71.93:3000",
    "http://192.168.71.93:3001",
    "http://192.168.71.93:8000",
    "http://10.129.150.25:3000",
    "http://10.129.150.25:3001",
    "http://10.129.150.25:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatInput(BaseModel):
    user_message: str

class RAGInput(BaseModel):
    file_path: str
    file_name: str

@app.get("/api/")
async def health_check():
    return {"status": "ok"}

@app.post("/api/rag")
async def rag_endpoint(file: UploadFile = File(...)):
    try:
        from rag_core.rag import context_base
        response = context_base(file.file, file.filename)
        return {"message": response}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"RAG processing error: {str(e)}")

@app.post("/api/filedeletion")
async def file_deletion_endpoint(input_data: ChatInput):
    try:
        from rag_core.rag import file_deletion
        response = file_deletion(input_data.user_message)
        return {"message": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/query")
async def query_endpoint(input_data: ChatInput):
    try:
        from rag_core.rag import response_generation
        response, context = response_generation(input_data.user_message)
        return {"bot_response": response, "context": context}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    index_path = os.path.join(frontend_path, "index.html")
    return FileResponse(index_path)