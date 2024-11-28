import os

class Config:
    # Cấu hình MQTT
    MQTT_BROKER = "06a3f96beed14b778927addb52b4de68.s1.eu.hivemq.cloud"
    MQTT_PORT = 8883
    MQTT_USERNAME = "Quan532003"
    MQTT_PASSWORD = "Quan532003@"
    
    # Các topic MQTT
    PUMP_TOPIC = "dieukhienbom"
    SENSOR_TOPIC = "cambien/duLieu"

    # Đường dẫn model
    MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model', 'best.pt')

    # Thư mục lưu ảnh
    IMAGES_DIR = os.path.join(os.path.dirname(__file__), '..', 'images')
    os.makedirs(IMAGES_DIR, exist_ok=True)