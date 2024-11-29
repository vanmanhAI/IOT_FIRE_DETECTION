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
from app.websocket import websocket_server

# Flask app setup
app = Flask(__name__)

current_mqtt_client = None

# Function to run Flask server
async def run_flask():
  config = Config()
  config.bind = ["0.0.0.0:5000"]  # Cấu hình địa chỉ và cổng
  await serve(app, config)


# MQTT client runner
async def run_mqtt():
  global current_mqtt_client
  current_mqtt_client = init_mqtt_client(asyncio.get_event_loop())
  current_mqtt_client.connect("06a3f96beed14b778927addb52b4de68.s1.eu.hivemq.cloud", 
                              8883, 60)
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
