import asyncio
import websockets
from PIL import Image, UnidentifiedImageError
from io import BytesIO
import json

connected_clients = set()
data_queue = asyncio.Queue() 

async def handle_connection(websocket, *_):
  print(f"Client connected: {websocket.remote_address}")
  connected_clients.add(websocket)  # Thêm client vào danh sách
  async for message in websocket:
    try:
      print(f"Received message: {message}")
      
    except UnidentifiedImageError as e:
      print(f"Failed to decode image: {e}")
    except Exception as e:
      print(f"An error occurred: {e}")
    finally:
        connected_clients.remove(websocket)  # Xóa client khi ngắt kết nối
        print(f"Client disconnected: {websocket.remote_address}")

async def send_data():
    while True:
        data = await data_queue.get()
        if data is None:
            break  # Kết thúc nếu nhận được None
        if connected_clients:  # Kiểm tra có client nào kết nối không
            message = json.dumps(data)
            await asyncio.wait([client.send(message) for client in connected_clients])

# async def websocket_server():
#     print("Starting WebSocket server on ws://0.0.0.0:3001")
#     async with websockets.serve(handle_connection, '0.0.0.0', 3001):
#         await asyncio.Future()  # Keeps the server running

async def websocket_server():
    print("Starting WebSocket server on ws://0.0.0.0:3001")
    server = await websockets.serve(handle_connection, '0.0.0.0', 3001)
    # sender = asyncio.create_task(send_data())
    await server.wait_closed()
    # await sender