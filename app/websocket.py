import asyncio
import websockets
from PIL import Image, UnidentifiedImageError
from io import BytesIO

connected_clients = set()

async def handle_connection(websocket, *_):
  print(f"Client connected: {websocket.remote_address}")
  async for message in websocket:
    try:
      image = Image.open(BytesIO(message))
      image.save("image.jpg")
      print(f"Received and saved image, size: {len(message)} bytes")

      await websocket.send("Image received successfully")
      
    except UnidentifiedImageError as e:
      print(f"Failed to decode image: {e}")
    except Exception as e:
      print(f"An error occurred: {e}")

async def broadcast(message):
    if connected_clients:
        await asyncio.gather(*[
            client.send(message) for client in connected_clients
            if not client.closed
        ])
        print("--------------------------------------------------------------------\n\n")
        print("Data broadcasted to all connected clients.")
        print("\n\n--------------------------------------------------------------------")
    else:
        print("No clients connected to broadcast.")

async def websocket_server():
    print("Starting WebSocket server on ws://0.0.0.0:3001")
    async with websockets.serve(handle_connection, '0.0.0.0', 3001):
        await asyncio.Future()  # Keeps the server running
