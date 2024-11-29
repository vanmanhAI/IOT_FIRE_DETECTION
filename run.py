import asyncio
from flask import Flask, jsonify, request
from hypercorn.asyncio import serve
from hypercorn.config import Config
import websockets
from io import BytesIO
from PIL import Image, UnidentifiedImageError
from app.mqtt import init_mqtt_client  # Import MQTT client từ mqtt.py
from app.routes import main_bp
from app.utils import get_image_stream

# Flask app setup
app = Flask(__name__)

current_mqtt_client = None

# Function to run Flask server
async def run_flask():
  config = Config()
  config.bind = ["0.0.0.0:5000"]  # Cấu hình địa chỉ và cổng
  await serve(app, config)

# WebSocket server
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

async def websocket_server():
  print("Starting WebSocket server on ws://0.0.0.0:3001")
  async with websockets.serve(handle_connection, '0.0.0.0', 3001):
    await asyncio.Future()  # Keeps the server running

# MQTT client runner
async def run_mqtt():
  global current_mqtt_client
  current_mqtt_client = init_mqtt_client()
  current_mqtt_client.connect("06a3f96beed14b778927addb52b4de68.s1.eu.hivemq.cloud", 8883, 60)
  current_mqtt_client.loop_start()  # Start MQTT loop in background
  await asyncio.sleep(1)  # Keep coroutine alive to allow other tasks to run
  
# Function to run image stream
async def run_image_stream():
    global current_mqtt_client
    if current_mqtt_client is None:
        print("MQTT client is not initialized.")
        return
    # Tạo một task riêng cho get_image_stream
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, get_image_stream, current_mqtt_client)

# Main function to run all components
async def main():
  app.register_blueprint(main_bp)  
  loop = asyncio.get_running_loop()
  await asyncio.gather(
    run_flask(),          # Flask server
    websocket_server(),   # WebSocket server
    run_mqtt(),
    run_image_stream()  # MQTT client
  )

if __name__ == "__main__":
  asyncio.run(main())
