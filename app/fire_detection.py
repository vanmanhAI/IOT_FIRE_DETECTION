from ultralytics import YOLO
from PIL import Image
from io import BytesIO
from .config import Config

class FireDetection:
    def __init__(self):
        self.model = YOLO(Config.MODEL_PATH)

    def detect_fire(self, image_path):
        try:
          image = Image.open(image_path)
          results = self.model.predict(image, show=False, imgsz=240)
          
          # Phân tích kết quả
          fire_detected = len(results[0].boxes) > 0
          
          # Vẽ các bounding box
          img_with_boxes = results[0].plot()
          
          return {
              'fire_detected': fire_detected,
              'num_detections': len(results[0].boxes),
              'image_path': image_path
          }
        except Exception as e:
          print(f"Fire detection error: {e}")
          return None