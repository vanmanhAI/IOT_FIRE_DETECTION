# run.py
import asyncio
import json
from io import BytesIO
from PIL import Image, UnidentifiedImageError
from flask import Flask, jsonify
from flask_cors import CORS
from hypercorn.asyncio import serve
from hypercorn.config import Config
import websockets

# Import các module nội bộ
from app.mqtt import init_mqtt_client
from app.routes import main_bp

# Khởi tạo Flask app
app = Flask(__name__)
CORS(app)
app.register_blueprint(main_bp)

# WebSocket clients (for broadcasting)
connected_websockets = set()

# Cấu hình Flask server
async def run_flask():
    config = Config()
    config.bind = ["0.0.0.0:5000"]  # Cấu hình địa chỉ và cổng
    print("Starting Flask server on http://0.0.0.0:5000")
    await serve(app, config)

# WebSocket handler
async def handle_websocket_connection(websocket):
    print(f"Client connected: {websocket.remote_address}")
    connected_websockets.add(websocket)
    try:
        async for message in websocket:
            try:
                image = Image.open(BytesIO(message))
                image.save("image.jpg")
                print(f"Received and saved image, size: {len(message)} bytes")
            except UnidentifiedImageError as e:
                print(f"Failed to decode image: {e}")
    finally:
        connected_websockets.remove(websocket)

# WebSocket server
async def websocket_server():
    print("Starting WebSocket server on ws://0.0.0.0:3001")
    async with websockets.serve(handle_websocket_connection, '0.0.0.0', 3001):
        await asyncio.Future()  # Giữ server chạy vô thời hạn


# WebSocket broadcast (revised)
async def websocket_broadcast(data):
    for websocket in set(connected_websockets): # Iterate over a copy to avoid issues if clients disconnect during iteration
        try:
            await websocket.send(json.dumps(data))
        except websockets.exceptions.ConnectionClosed:
            # Handle closed connections gracefully
            print(f"WebSocket client disconnected: {websocket.remote_address}")
            connected_websockets.discard(websocket)  # Remove disconnected client



# MQTT client runner (using run_in_executor)
# run.py (relevant part)
async def run_mqtt():
    client = init_mqtt_client()
    client.connect("06a3f96beed14b778927addb52b4de68.s1.eu.hivemq.cloud", 8883, 60)

    def on_message(client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode('utf-8'))
            print(f"MQTT message received: {data}")

            # Get the running loop
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:  # If no running loop, create a new one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            loop.call_soon_threadsafe(websocket_broadcast, data) # Schedule the call



        except json.JSONDecodeError:
            print("Failed to decode MQTT message payload.")
        except Exception as e:
            print(f"Error in on_message: {e}")

    client.on_message = on_message

    client.loop_start()
    print("MQTT client connected and running.")
    await asyncio.Future() # Keep the MQTT client running

# Main function to run all services
async def main():
    await asyncio.gather(
        run_flask(),
        websocket_server(),
        run_mqtt()
    )


if __name__ == "__main__":
    asyncio.run(main())