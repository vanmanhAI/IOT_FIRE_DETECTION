import asyncio
from flask import Flask, jsonify, request
from hypercorn.asyncio import serve
from hypercorn.config import Config
import websockets
from io import BytesIO
from PIL import Image, UnidentifiedImageError
from app.mqtt import init_mqtt_client  # Import MQTT client từ mqtt.py

# Flask app setup
app = Flask(__name__)

@app.route('/hello', methods=['GET'])
def hello():
    return jsonify({"message": "Hello World!"}), 200

@app.route('/light', methods=['POST'])
def receive_light_data():
    data = request.get_json()
    if not data:
      return jsonify({"error": "No data received"}), 400

    light_state = data.get("light_value")
    if light_state is None:
      return jsonify({"error": "Invalid data format"}), 400

    print(f"Light state received: {light_state}")
    return jsonify({"message": "Data received successfully", "light_value": light_state}), 200

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
  client = init_mqtt_client()
  client.connect("06a3f96beed14b778927addb52b4de68.s1.eu.hivemq.cloud", 8883, 60)
  client.loop_start()  # Start MQTT loop in background
  await asyncio.sleep(1)  # Keep coroutine alive to allow other tasks to run

# Main function to run all components
async def main():
  loop = asyncio.get_running_loop()
  await asyncio.gather(
    run_flask(),          # Flask server
    websocket_server(),   # WebSocket server
    run_mqtt()            # MQTT client
  )

if __name__ == "__main__":
  asyncio.run(main())
