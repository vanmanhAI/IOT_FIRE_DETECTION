import asyncio
import threading
import json
from flask import Flask, Response
from hypercorn.asyncio import serve
from hypercorn.config import Config
import paho.mqtt.client as mqtt
from ultralytics import YOLO
import time
import cv2
from calculate import TinhToan
import websockets
from app.database import save_history_fire_data, save_log, get_history_fire_data, get_logs

#=========================================INIT=============================================
#Initialize Flask app
app = Flask(__name__)

# MQTT Topics
PUMP_TOPIC = "dieukhienbom"
GENERAL_TOPIC = "cambien/duLieu"

# Global variables
mqtt_client = None
previous_fire_level = "safe"
percent_of_fire = 0

# Load the model
model = YOLO("app/model/best2.pt")

# Set to store connected WebSocket clients
connected_websockets = set()
websockets_lock = threading.Lock()

# Event loop reference
loop = None

def classify_fire_level(fire_percentage):
    if fire_percentage < 30:
        return "safe"          # An toàn
    elif fire_percentage < 60:
        return "warning"       # Nguy cơ
    elif fire_percentage < 80:
        return "danger"        # Nguy hiểm
    else:
        return "critical"      # Cực kỳ nguy hiểm

# ======================================FLASK==============================================
# Flask route for streaming
@app.route('/stream')
def stream():
    return Response(get_image_stream_client(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Function to get image stream and process data
def get_image_stream_client():
    global mqtt_client, percent_of_fire

    results = model("http://172.20.10.7./stream", stream=True)
    fire_detected_time = None

    for result in results:
        # Get the frame with detections plotted
        frame = result.plot()

        # Check if any detections are present
        if result.boxes is not None and len(result.boxes) > 0:
            xywh = result.boxes.xywh[0].tolist()
            print(result.boxes.conf.tolist()[0])
            percent_of_fire = result.boxes.conf.tolist()[0]
            x_center = xywh[0] / result.orig_shape[1]
            y_center = xywh[1] / result.orig_shape[0]
            w = xywh[2] / result.orig_shape[1]
            h = xywh[3] / result.orig_shape[0]
            print("--------------------------------------------------------------------")
            print(f"Fire detected at ({x_center:.2f}, {y_center:.2f})")
            print(f"Width: {w:.2f}, Height: {h:.2f}")
            print("--------------------------------------------------------------------")

            if fire_detected_time is None:
                fire_detected_time = time.time()
                
            elif time.time() - fire_detected_time >= 5:
                # Calculate servo angles
                data_to_send = TinhToan(x_center, y_center, w)
                
                # Send data to MQTT broker
                if mqtt_client is not None and mqtt_client.is_connected():
                    mqtt_client.publish(PUMP_TOPIC, json.dumps(data_to_send))
                    fire_detected_time = None  
                    print("SENDSENDSENDSENDSENDSENDSENDSENDSENDSENDSENDSENDSENDSEND")  
                else:
                    print("MQTT client is not connected.")
        else:
            fire_detected_time = None
            percent_of_fire = 0

        # Encode frame as JPEG
        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            print("Failed to encode frame.")
            continue

        # Yield frame in byte format for streaming
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')

# get all record from historyFire table in mongodb
@app.route('/history', methods=['GET'])
def get_history():
    return json.dumps(get_history_fire_data())

# get all record from logs table in mongodb
@app.route('/logs')
def get_log_history():
    return json.dumps(get_logs())

# ========================================MQTT=============================================

# MQTT client setup
def init_mqtt_client():
    global percent_of_fire
    client = mqtt.Client()
    client.username_pw_set("Quan532003", "Quan532003@")
    client.tls_set()
    
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
            client.subscribe(GENERAL_TOPIC)
        else:
            print(f"Failed to connect, return code {rc}")

    def on_message(client, userdata, msg):
        global previous_fire_level, loop

        try:
            data = json.loads(msg.payload.decode('utf-8'))

            print("--------------------------------------------------------------------")
            print(f"Received: {data['lua1']} {data['lua2']} {data['lua3']} {data['khoi']}")
            print("--------------------------------------------------------------------")

            # Process sensor data
            w_flame = 0.55
            w_ai = 0.35
            w_khoi = 0.1

            lua1 = data['lua1']
            lua2 = data['lua2']
            lua3 = data['lua3']
            khoi = data['khoi']

            normalized_khoi = khoi / 1200

            flame_average = (lua1 + lua2 + lua3) / 3

            fire_percentage = (flame_average * w_flame + normalized_khoi * w_khoi + percent_of_fire * w_ai) * 100

            # Save data to database
            save_history_fire_data(lua1, lua2, lua3, normalized_khoi, fire_percentage, percent_of_fire)

            # Classify fire level
            current_fire_level = classify_fire_level(fire_percentage)
            if current_fire_level != previous_fire_level:
                save_log(previous_fire_level, current_fire_level)
                previous_fire_level = current_fire_level
            
            # Prepare data to send via WebSocket
            send_data = {
                "lua1": lua1,
                "lua2": lua2,
                "lua3": lua3,
                "khoi": khoi,
                "fire_percentage": fire_percentage,
                "percent_of_fire": percent_of_fire,
                "fire_level": current_fire_level
            }

            # Send data to all connected WebSocket clients
            with websockets_lock:
                for ws in connected_websockets.copy():
                    try:
                        asyncio.run_coroutine_threadsafe(ws.send(json.dumps(send_data)), loop)
                    except Exception as e:
                        print(f"WebSocket error: {e}")
                        connected_websockets.remove(ws)

        except Exception as e:
            print(f"MQTT message processing error: {e}")

    client.on_connect = on_connect
    client.on_message = on_message
    return client

# ======================================WEBSOCKET===========================================
async def websocket_handler(websocket):
    global connected_websockets
    # Register WebSocket connection
    with websockets_lock:
        connected_websockets.add(websocket)
    try:
        async for message in websocket:
            # Handle messages from client if needed
            pass
    except websockets.exceptions.ConnectionClosed:
        print("WebSocket connection closed")
    finally:
        # Remove WebSocket when the connection is closed
        with websockets_lock:
            connected_websockets.remove(websocket)

# ==============================================RUN========================================
# Function to run Flask server
async def run_flask():
    config = Config()
    config.bind = ["0.0.0.0:5000"]  # Configure host and port
    await serve(app, config)

# Main function to run all components
async def main():
    global mqtt_client, loop
    mqtt_client = init_mqtt_client()
    mqtt_client.connect("06a3f96beed14b778927addb52b4de68.s1.eu.hivemq.cloud", 8883, 60)
    mqtt_client.loop_start()  # Start MQTT loop in background

    # Lấy event loop hiện tại
    loop = asyncio.get_running_loop()

    # Start WebSocket server
    websocket_server = websockets.serve(websocket_handler, "0.0.0.0", 8765)

    # Chạy Flask và WebSocket server đồng thời
    await asyncio.gather(
        websocket_server,
        run_flask()
    )

if __name__ == "__main__":
    asyncio.run(main())