import asyncio
import websockets
from PIL import Image
from io import BytesIO
import json

connected_clients = set()

async def handle_connection(websocket, *_):
  print(f"Client connected: {websocket.remote_address}")
  connected_clients.add(websocket)
  async for message in websocket:
    try:
      image = Image.open(BytesIO(message))
      image.save("image.jpg")
      print(f"Received and saved image")
    except Exception as e:
      print(f"Error processing image: {e}")
      
async def send_message(message):
    if connected_clients:
      await asyncio.wait([client.send(message) for client in connected_clients])

async def websocket_server():
  print("Starting WebSocket server on ws://0.0.0.0:3001")
  async with websockets.serve(handle_connection, "0.0.0.0", 3001):
    await asyncio.Future()

async def send_mqtt_data_to_clients(data):
  if connected_clients:
    message = json.dumps(data)
    await asyncio.wait([client.send(message) for client in connected_clients])
