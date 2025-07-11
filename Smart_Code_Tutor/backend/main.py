from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import asyncio
import json
from typing import Dict, List
import os
from dotenv import load_dotenv

from .code_executor import execute_code
from .rag_system import get_code_explanation
from .websocket_manager import ConnectionManager

load_dotenv()

app = FastAPI(title="Smart Code Tutor API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
manager = ConnectionManager()

@app.get("/")
async def root():
    return {"message": "Smart Code Tutor API is running"}

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "execute_code":
                await handle_code_execution(websocket, message, client_id)
            elif message["type"] == "get_explanation":
                await handle_explanation_request(websocket, message, client_id)
                
    except WebSocketDisconnect:
        manager.disconnect(client_id)

async def handle_code_execution(websocket: WebSocket, message: dict, client_id: str):
    code = message["code"]
    language = message["language"]
    
    # Send execution start message
    await websocket.send_text(json.dumps({
        "type": "execution_start",
        "message": f"Executing {language} code..."
    }))
    
    try:
        # Execute code and stream results
        async for result in execute_code(code, language):
            await websocket.send_text(json.dumps({
                "type": "execution_result",
                "data": result
            }))
            
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "execution_error",
            "error": str(e)
        }))

async def handle_explanation_request(websocket: WebSocket, message: dict, client_id: str):
    code = message["code"]
    language = message["language"]
    context = message.get("context", "")
    
    try:
        # Get RAG-based explanation
        explanation = await get_code_explanation(code, language, context)
        await websocket.send_text(json.dumps({
            "type": "explanation_result",
            "explanation": explanation
        }))
        
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "explanation_error",
            "error": str(e)
        }))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 