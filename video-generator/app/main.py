from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from redis import Redis
from rq import Queue, Retry
import router  # Router to dispatch models
import uuid
import logging
import asyncio
from pydantic import BaseModel
from typing import Optional, Dict, Any

app = FastAPI()
logging.basicConfig(level=logging.INFO)

class VideoRequest(BaseModel):
    prompt: str
    model_name: str
    params: Optional[Dict[str, Any]] = {}  # Dynamic parameters for each model

# Connect to Redis
redis_conn = Redis(host="redis", port=6379, decode_responses=True)

# Video Queue
queue = Queue("video_requests", connection=redis_conn)

# WebSocket connections
active_connections = {}
client_result_keys = set()

def generate_client_id():
    return str(uuid.uuid4())

@app.websocket("/video-ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    active_connections[client_id] = websocket
    logging.info(f"WebSocket connected: {client_id}")

    try:
        while True:
            await websocket.send_text("ping")
            await asyncio.sleep(15)
            await websocket.receive_text()  # Keep connection alive
    except WebSocketDisconnect:
        active_connections.pop(client_id, None)
        logging.info(f"WebSocket disconnected: {client_id}")

@app.post("/generate-video/")
async def generate_video(request: VideoRequest):
    """Queue a video generation job with dynamic parameters."""
    if not request.prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    client_id = generate_client_id()
    client_result_keys.add(client_id)

    job_args = {
        "model_name": request.model_name,
        "prompt": request.prompt,
        "client_id": client_id,
        "params": request.params
    }

    job = queue.enqueue(router.run_model_task, **job_args, retry=Retry(max=40))
    logging.info(f"Video job queued for client {client_id}")
    return {"job_id": job.id, "client_id": client_id, "message": "Video generation job queued."}

@app.get("/video-result/{client_id}")
async def get_video_result(client_id: str):
    result = redis_conn.get(f"result:{client_id}")
    if result:
        return {"status": "done", "result": result}

    return {"status": "pending"}

async def monitor_results():
    while True:
        await asyncio.sleep(2)
        for client_id in list(client_result_keys):
            result = redis_conn.get(f"result:{client_id}")
            if result:
                websocket = active_connections.get(client_id)
                if websocket:
                    try:
                        await websocket.send_text(f"Result Ready: {result}")
                        logging.info(f"Video result pushed to client {client_id}")
                    except Exception as e:
                        logging.error(f"Failed to send video result to {client_id}: {e}")
                client_result_keys.remove(client_id)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(monitor_results())
