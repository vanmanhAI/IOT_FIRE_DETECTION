import asyncio
import websockets
from PIL import Image, UnidentifiedImageError
from io import BytesIO

connected_clients = set()

async def handle_connection(websocket, *_):
  print(f"Client connected: {websocket.remote_address}")
  connected_clients.add(websocket)  # Thêm client vào danh sách
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
    finally:
        connected_clients.remove(websocket)  # Xóa client khi ngắt kết nối
        print(f"Client disconnected: {websocket.remote_address}")

async def send_message_to_client(client, message):
    try:
        await client.send(message)
    except Exception as e:
        print(f"Error sending message to client {client.remote_address}: {e}")

async def websocket_server():
    print("Starting WebSocket server on ws://0.0.0.0:3001")
    async with websockets.serve(handle_connection, '0.0.0.0', 3001):
        await asyncio.Future()  # Keeps the server running