from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.models import ChatRequest, ChatResponse, ChatMessage
from app.agent import app as agent_app
from langchain_core.messages import HumanMessage, AIMessage
import shutil
import os

app = FastAPI(title="AI Doctor Companion")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "AI Doctor Companion API is running"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # Convert history to LangChain messages
    messages = []
    for msg in request.history:
        if msg.role == "user":
            messages.append(HumanMessage(content=msg.content))
        else:
            messages.append(AIMessage(content=msg.content))
    
    # Add current message
    messages.append(HumanMessage(content=request.message))
    
    # Invoke agent
    # We initialize state with the messages
    initial_state = {"messages": messages, "symptoms": [], "reports_uploaded": False, "diagnosis_ready": False}
    
    try:
        result = agent_app.invoke(initial_state)
        last_message = result["messages"][-1]
        return ChatResponse(response=last_message.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        os.makedirs("uploads", exist_ok=True)
        file_path = f"uploads/{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return {"message": "File uploaded successfully", "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
