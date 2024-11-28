import asyncio
import websockets
from PIL import Image
from io import BytesIO
import json
import logging

# Cấu hình logging chi tiết
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

connected_clients = set()

async def handle_connection(websocket, path):
    try:
        # Thêm client vào danh sách kết nối
        connected_clients.add(websocket)
        logger.info(f"Client connected: {websocket.remote_address}")
        try:
            async for message in websocket:
                try:
                    # Thử parse JSON đầu tiên
                    try:
                        data = json.loads(message)
                        logger.info(f"Received JSON: {data}")
                        await websocket.send(json.dumps({"status": "JSON received"}))
                    except json.JSONDecodeError:
                        # Nếu không phải JSON, thử xử lý như ảnh
                        image = Image.open(BytesIO(message))
                        image.save("images/image.jpg")
                        logger.info("Received and saved image")
                        await websocket.send(json.dumps({"status": "Image received"}))
                
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    await websocket.send(json.dumps({"error": str(e)}))
        
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed by client")
        
        finally:
            # Loại bỏ client khỏi danh sách kết nối
            connected_clients.discard(websocket)
    
    except Exception as e:
        logger.error(f"Connection handler error: {e}")

async def websocket_server():
    # Sử dụng cấu hình server mạnh hơn
    server = await websockets.serve(
        handle_connection, 
        "0.0.0.0",  # Lắng nghe trên tất cả các giao diện
        3001,
        ping_interval=20,  # Thêm ping interval để giữ kết nối
        ping_timeout=20,
        close_timeout=10
    )
    
    logger.info("WebSocket server started on ws://0.0.0.0:3001")
    
    # Giữ server luôn chạy
    await server.wait_closed()


async def send_mqtt_data_to_clients(data):
  if connected_clients:
    message = json.dumps(data)
    await asyncio.wait([client.send(message) for client in connected_clients])
