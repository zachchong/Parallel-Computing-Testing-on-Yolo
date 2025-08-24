import asyncio
import websockets
import os
import datetime

async def send_image(image_file, websocket):
    nowA = datetime.datetime.now()
    print(f"Read: {image_file} {nowA}")
    with open(image_file, "rb") as f:
        image_data = f.read()
        await websocket.send(image_data)
        nowB = datetime.datetime.now()
        print(f"Sent: {image_file} {nowB}") 

async def main():
    image_dir = "./images"  
    image_files = [os.path.join(image_dir, f) for f in os.listdir(image_dir) if os.path.isfile(os.path.join(image_dir, f))]

    uri = "ws://localhost:4000/upload"
    tasks = []
    async with websockets.connect(uri) as websocket:
        for image_file in image_files:
            task = asyncio.create_task(send_image(image_file, websocket))
            tasks.append(task)

        await asyncio.gather(*tasks)
        await websocket.send("done")
        print("All images sent")

asyncio.run(main())
