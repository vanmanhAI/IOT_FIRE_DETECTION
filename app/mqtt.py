import paho.mqtt.client as mqtt
import json
from app.database import get_image_stream, save_history_fire_data
import asyncio
from app.websocket import data_queue

PUMP_TOPIC = "dieukhienbom"
GENERAL_TOPIC = "cambien/duLieu"

def init_mqtt_client(loop):
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
        try:
            data = json.loads(msg.payload.decode('utf-8'))

            print("--------------------------------------------------------------------\n")
            print(f"Received: {data['lua1']} {data['lua2']} {data['lua3']} {data['khoi']}\n")
            print("--------------------------------------------------------------------")
            # Gửi dữ liệu đến WebSocket
            asyncio.run_coroutine_threadsafe(data_queue.put({
                'lua1': data['lua1'],
                'lua2': data['lua2'],
                'lua3': data['lua3'],
                'khoi': data['khoi']
            }), loop)
            
            # Lưu dữ liệu vào historyFireCollection
            save_history_fire_data(data['lua1'], data['lua2'], data['lua3'], data['khoi'], data['chay'], data['detect'])
            
            # Lưu dữ liệu vào collection
            get_image_stream(client, data)
            
            # Gửi dữ liệu đến WebSocket
        except Exception as e:
            print(f"MQTT message processing error: {e}")

    client.on_connect = on_connect
    client.on_message = on_message
    return client