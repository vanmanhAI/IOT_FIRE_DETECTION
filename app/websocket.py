import asyncio
import websockets
from PIL import Image, UnidentifiedImageError
from io import BytesIO
import json
# Tập hợp client kết nối cho ảnh
connected_image_clients = set()

# Tập hợp client kết nối cho dữ liệu real-time
connected_data_clients = set()

# Hàm xử lý kết nối chung
async def handle_connection(websocket):
    print(f"path: {websocket.request.path}")
    
    if websocket.request.path == "/":
        print(f"[Data Server] Client connected: {websocket.remote_address}")
        connected_data_clients.add(websocket)
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    print(f"[Data Server] Received data: {data}")
                except json.JSONDecodeError as e:
                    print(f"[Data Server] Failed to decode JSON: {e}")
                except Exception as e:
                    print(f"[Data Server] An error occurred: {e}")
        except websockets.exceptions.ConnectionClosed as e:
            print(f"[Data Server] Connection closed: {e}")
        finally:
            connected_data_clients.remove(websocket)
            print(f"[Data Server] Client disconnected: {websocket.remote_address}")
    else:
        print(f"[Image Server] Client connected: {websocket.remote_address}")
        connected_image_clients.add(websocket)
        try:
            async for message in websocket:
                try:
                    image = Image.open(BytesIO(message))
                    image.save("image.jpg")
                    print(f"[Image Server] Received and saved image, size: {len(message)} bytes")
                    await websocket.send("Image received successfully")
                except UnidentifiedImageError as e:
                    print(f"[Image Server] Failed to decode image: {e}")
                    await websocket.send("Failed to decode image.")
                except Exception as e:
                    print(f"[Image Server] An error occurred: {e}")
                    await websocket.send("An error occurred while processing the image.")
        except websockets.exceptions.ConnectionClosed as e:
            print(f"[Image Server] Connection closed: {e}")
        finally:
            connected_image_clients.remove(websocket)
            print(f"[Image Server] Client disconnected: {websocket.remote_address}")


async def broadcast(message):
    if connected_data_clients:
        print(f"TESTTTTTT - Số lượng client: {len(connected_data_clients)}")
        for client in connected_data_clients:
          print(f"Client type: {type(client)}")
          tasks = []
          for client in connected_data_clients:
            tasks.append(send_message_to_client(client, message))
          await asyncio.gather(*tasks)
          print("--------------------------------------------------------------------\n\n")
          print("Data broadcasted to all connected clients.")
          print("\n\n--------------------------------------------------------------------")
        
    else:
        print("No clients connected to broadcast.")

async def send_message_to_client(client, message):
    try:
        await client.send(message)
    except Exception as e:
        print(f"Error sending message to client {client.remote_address}: {e}")

async def websocket_server():
    print("Starting WebSocket server on ws://0.0.0.0:3001")
    async with websockets.serve(handle_connection, '0.0.0.0', 3001):
        await asyncio.Future()  # Keeps the server running