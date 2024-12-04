from PIL import Image
from io import BytesIO
import json
from ultralytics import YOLO
import math
import time
import cv2 as cv
from app.utils import save_history_fire_data

# Load a model
model = YOLO("app/model/best.pt")
# LUA1, LUA2, LUA3, KHOI, %CHAY, %DETECT

def get_image_stream_client():
  while True:
    try:
      with open("image.jpg", "rb") as f:
        image_bytes = f.read()
      image = Image.open(BytesIO(image_bytes))
  
      results = model.predict(image, show=False, imgsz=240)
      result = results[0]

      img = result.plot()
      imageRGB = cv.cvtColor(img, cv.COLOR_BGR2RGB)
      image = Image.fromarray(imageRGB)

      img_io = BytesIO()
      image.save(img_io, 'JPEG')
      img_io.seek(0)
      yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + img_io.read() + b'\r\n')
    except Exception as e:
      print("Error reading image:", e)
      yield b''

def get_image_stream(mqtt_client, data):
  fire_detected_start_time = None
  
  w_flame = 0.5
  w_khoi = 0.1
  w_ai = 0.4
  
  lua1 = data['lua1']
  lua2 = data['lua2']
  lua3 = data['lua3']
  khoi = data['khoi']
  flame_average = (lua1 + lua2 + lua3) / 3
  
  normalized_khoi = (khoi - 200) / (10000 - 200)
  normalized_khoi = max(0, min(normalized_khoi, 1))  # Đảm bảo giá trị trong khoảng [0,1]
  
  while True:
    try:
      with open("image.jpg", "rb") as f:
        image_bytes = f.read()
      image = Image.open(BytesIO(image_bytes))

      results = model.predict(image, show=False, imgsz=240)
      result = results[0]
      
      print(results)      

      if result.boxes is None or len(result.boxes) == 0:
        print("No objects detected.")
        fire_detected_start_time = None
        fire_percentage = (flame_average * w_flame + normalized_khoi * w_khoi) * 100  # Chuyển sang phần trăm
        # save to DB
        save_history_fire_data(lua1, lua2, lua3, khoi, fire_percentage, 0)
      else:
        # Phát hiện lửa
        confidence_scores = result.boxes.conf.tolist()
        print(f"Confidence scores: {confidence_scores}")
        
        confidence = confidence_scores[0] * 100  # Chuyển đổi sang phần trăm
        print(f"Fire detection confidence: {confidence:.2f}%")
        normalized_confidence = confidence / 100
        
        fire_percentage = (
          flame_average * w_flame +
          normalized_khoi * w_khoi +
          normalized_confidence * w_ai
        ) * 100  # Chuyển sang phần trăm
        
        # SAVE TO DB
        save_history_fire_data(lua1, lua2, lua3, khoi, fire_percentage, confidence)
        
        if fire_detected_start_time is None:
          fire_detected_start_time = time.time()
          print("Fire detected, starting timer...")
        else:
          
          # Tính thời gian đã phát hiện lửa
          elapsed_time = time.time() - fire_detected_start_time
          print(f"Fire detected for {elapsed_time:.2f} seconds")
          if elapsed_time >= 5:
            xywh = result.boxes.xywh[0].tolist()
            x_center = xywh[0] / result.orig_shape[1]
            y_center = xywh[1] / result.orig_shape[0]

            print(f"Fire detected at ({x_center:.2f}, {y_center:.2f})")

            data = TinhToan(x_center, y_center)

            if mqtt_client.is_connected():
              print("Sending data to MQTT...")
              mqtt_client.publish("dieukhienbom", json.dumps(data))
              
              # Reset thời gian sau khi gửi
              fire_detected_start_time = None
            else:
              print("MQTT client not connected.")

    except Exception as e:
      print("Error reading image:", e)

def TinhToan(x: float, y: float):
    tmp1 = math.atan(abs(x - 0.76) * 25.0 / 30.0)
    alpha_degree = math.degrees(tmp1)
    goc1 = 45
    if x <= 0.76:
      goc1 = 100 - alpha_degree - 20 * (0.76 - x) / 0.76
    else:
      goc1 = 100 + alpha_degree
    print(goc1)
    tmp2 = math.atan(abs(y - 1) * 25.0 / 30.0)
    alpha_degree = math.degrees(tmp2)
    goc2 = 90 - alpha_degree
    # print(goc2)
    goc2From = goc2 - 30
    goc2To = goc2 + 30

    return {
        "goc1": int(goc1),
        "goc2From": int(goc2From),
        "goc2To": int(goc2To)
    }
    
def classify_fire_level(fire_percentage):
    if fire_percentage < 30:
        return "safe"
    elif fire_percentage < 60:
        return "caution"
    elif fire_percentage < 90:
        return "danger"
    else:
        return "dangerous"
  # gui len mqtt voi topic la dieukhienbom {"goc1": goc1, "goc2From": 90, "goc2To": 90}
