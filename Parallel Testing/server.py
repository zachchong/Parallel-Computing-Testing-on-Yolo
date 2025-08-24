import asyncio
import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from io import BytesIO
import datetime
import time
import torch
from concurrent.futures import ThreadPoolExecutor

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = torch.hub.load('yolov5', 'custom', path=r'[Model]', source='local') 

def process_image(data):
    image = Image.open(BytesIO(data))
    nowA = datetime.datetime.now()
    results = model(image) 
    nowB = datetime.datetime.now()
    duration = nowB - nowA
    duration_ms = duration.total_seconds() *1000
    print(f"Process Duration: {duration_ms}ms")
    print(results)

async def async_process_image(data):
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as pool:
        await loop.run_in_executor(pool, process_image, data)

@app.websocket("/upload")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        tasks = []
        while True:
            data = await websocket.receive_bytes()
            if data == b"done":
                break
            now = datetime.datetime.now()
            print(f"Image received at {now}")
            task = asyncio.create_task(async_process_image(data))
            tasks.append(task)

        if tasks:
            await asyncio.gather(*tasks)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await websocket.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000)
