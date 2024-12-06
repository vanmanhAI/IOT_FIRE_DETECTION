from PIL import Image
from io import BytesIO
import json
from ultralytics import YOLO
import math
import time
import cv2 as cv
from app.database import save_history_fire_data, save_log
from app.websocket import send_data

# Load a model
model = YOLO("app/model/best1.pt")
# Thêm biến toàn cục để lưu trạng thái fire_level trước đó
previous_fire_level = None

import cv2
from io import BytesIO
from PIL import Image
def get_image_stream_client():
    results = model("http://192.168.1.18/stream", stream=True)
    for result in results:
        # Get the frame with detections plotted
        frame = result.plot()
        
        # Encode frame as JPEG
        _, jpeg = cv2.imencode('.jpg', frame)
        
        # Yield frame in byte format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')

def get_image_stream(mqtt_client, data):
    print("Getting image stream...-----------------------------------")
    global previous_fire_level  # Ensure this is declared globally

    fire_detected_start_time = None

    w_flame = 0.5
    w_khoi = 0.1
    w_ai = 0.4

    lua1 = data['lua1']
    lua2 = data['lua2']
    lua3 = data['lua3']
    khoi = data['khoi']
    flame_average = (lua1 + lua2 + lua3) / 3

    # send_data(data)

    normalized_khoi = (khoi - 200) / (10000 - 200)
    normalized_khoi = max(0, min(normalized_khoi, 1))  # Ensure value is between [0,1]

    results = model("http://192.168.1.18/stream", stream=True)
    for result in results:
        try:
            # Process detection results
            if result.boxes is None or len(result.boxes) == 0:
                print("No objects detected.")
                fire_detected_start_time = None
                fire_percentage = (flame_average * w_flame + normalized_khoi * w_khoi) * 100
                # Save to DB
                save_history_fire_data(lua1, lua2, lua3, khoi, fire_percentage, 0)

                fire_level = classify_fire_level(fire_percentage)
                # Compare with previous state
                if previous_fire_level != fire_level:
                    save_log(previous_fire_level, fire_level)
                    previous_fire_level = fire_level  # Update to new state
            else:
                xywh = result.boxes.xywh[0].tolist()
                x_center = xywh[0] / result.orig_shape[1]
                y_center = xywh[1] / result.orig_shape[0]
                print("--------------------------------------------------------------------\n")
                print(f"Fire detected at ({x_center:.2f}, {y_center:.2f})\n\n")
                print("--------------------------------------------------------------------\n")
                # Fire detected
                confidence_scores = result.boxes.conf.tolist()
                print(f"Confidence scores: {confidence_scores}")

                # Use the highest confidence score
                confidence = max(confidence_scores) * 100  # Convert to percentage
                print(f"Fire detection confidence: {confidence:.2f}%")
                normalized_confidence = confidence / 100

                fire_percentage = (
                    flame_average * w_flame +
                    normalized_khoi * w_khoi +
                    normalized_confidence * w_ai
                ) * 100  # Convert to percentage

                # Save to DB
                save_history_fire_data(lua1, lua2, lua3, khoi, fire_percentage, confidence)

                fire_level = classify_fire_level(fire_percentage)
                # Compare with previous state
                if previous_fire_level != fire_level:
                    save_log(previous_fire_level, fire_level)
                    previous_fire_level = fire_level  # Update to new state

                if fire_detected_start_time is None:
                    fire_detected_start_time = time.time()
                    print("Fire detected, starting timer...")
                else:
                    # Calculate elapsed time since fire was detected
                    elapsed_time = time.time() - fire_detected_start_time
                    print(f"Fire detected for {elapsed_time:.2f} seconds")
                    if elapsed_time >= 5:
                        xywh = result.boxes.xywh[0].tolist()
                        x_center = xywh[0] / result.orig_shape[1]
                        y_center = xywh[1] / result.orig_shape[0]

                        print("--------------------------------------------------------------------\n")
                        print(f"Fire detected at ({x_center:.2f}, {y_center:.2f})\n\n")
                        print("--------------------------------------------------------------------\n")

                        data_to_send = TinhToan(x_center, y_center)

                        if mqtt_client.is_connected():
                            print("Sending data to MQTT...")
                            mqtt_client.publish("dieukhienbom", json.dumps(data_to_send))

                            # Reset timer after sending data
                            fire_detected_start_time = None
                        else:
                            print("MQTT client not connected.")
        except Exception as e:
            print("Error processing frame:", e)
            continue  # Continue processing the next frame

# def get_image_stream_client():
#   try:
#     results = model("http://192.168.1.18/stream", stream=False, show=False)
#     for r in results:
#       frame = r.render()[0]
#       yield (b'--frame\r\n'
#               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
#   except ConnectionError as e:
#     print(f"ConnectionError: {e}")
#     yield b'--frame\r\nContent-Type: text/plain\r\n\r\nError: Unable to connect to stream\r\n'
  # while True:
  #   try:
  #     with open("image.jpg", "rb") as f:
  #       image_bytes = f.read()
  #     image = Image.open(BytesIO(image_bytes))
  
  #     results = model.predict(image, show=False, imgsz=240)
  #     result = results[0]

  #     img = result.plot()
  #     imageRGB = cv.cvtColor(img, cv.COLOR_BGR2RGB)
  #     image = Image.fromarray(imageRGB)

  #     img_io = BytesIO()
  #     image.save(img_io, 'JPEG')
  #     img_io.seek(0)
  #     yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + img_io.read() + b'\r\n')
  #   except Exception as e:
  #     print("Error reading image:", e)
  #     yield b''

# def get_image_stream(mqtt_client, data):
#   fire_detected_start_time = None
  
#   w_flame = 0.5
#   w_khoi = 0.1
#   w_ai = 0.4
  
#   lua1 = data['lua1']
#   lua2 = data['lua2']
#   lua3 = data['lua3']
#   khoi = data['khoi']
#   flame_average = (lua1 + lua2 + lua3) / 3

#   send_data(data)
  
#   normalized_khoi = (khoi - 200) / (10000 - 200)
#   normalized_khoi = max(0, min(normalized_khoi, 1))  # Đảm bảo giá trị trong khoảng [0,1]
  
#   while True:
#     try:
#       with open("image.jpg", "rb") as f:
#         image_bytes = f.read()
#       image = Image.open(BytesIO(image_bytes))

#       results = model.predict(image, show=False, imgsz=240)
#       result = results[0]
      
#       print(results)      

#       if result.boxes is None or len(result.boxes) == 0:
#         print("No objects detected.")
#         fire_detected_start_time = None
#         fire_percentage = (flame_average * w_flame + normalized_khoi * w_khoi) * 100  # Chuyển sang phần trăm
#         # save to DB
#         save_history_fire_data(lua1, lua2, lua3, khoi, fire_percentage, 0)
        
#         fire_level = classify_fire_level(fire_percentage)
#         # So sánh với trạng thái trước đó
#         if previous_fire_level != fire_level:
#             save_log(previous_fire_level, fire_level)
#             previous_fire_level = fire_level  # Cập nhật trạng thái mới
#       else:
#         # Phát hiện lửa
#         confidence_scores = result.boxes.conf.tolist()
#         print(f"Confidence scores: {confidence_scores}")
        
#         confidence = confidence_scores[0] * 100  # Chuyển đổi sang phần trăm
#         print(f"Fire detection confidence: {confidence:.2f}%")
#         normalized_confidence = confidence / 100
        
#         fire_percentage = (
#           flame_average * w_flame +
#           normalized_khoi * w_khoi +
#           normalized_confidence * w_ai
#         ) * 100  # Chuyển sang phần trăm
        
#         # SAVE TO DB
#         save_history_fire_data(lua1, lua2, lua3, khoi, fire_percentage, confidence)
        
#         fire_level = classify_fire_level(fire_percentage)
# # So sánh với trạng thái trước đó
#         if previous_fire_level != fire_level:
#             save_log(previous_fire_level, fire_level)
#             previous_fire_level = fire_level  # Cập nhật trạng thái mới
        
#         if fire_detected_start_time is None:
#           fire_detected_start_time = time.time()
#           print("Fire detected, starting timer...")
#         else:
          
#           # Tính thời gian đã phát hiện lửa
#           elapsed_time = time.time() - fire_detected_start_time
#           print(f"Fire detected for {elapsed_time:.2f} seconds")
#           if elapsed_time >= 5:
#             xywh = result.boxes.xywh[0].tolist()
#             x_center = xywh[0] / result.orig_shape[1]
#             y_center = xywh[1] / result.orig_shape[0]

#             print(f"Fire detected at ({x_center:.2f}, {y_center:.2f})")

#             data = TinhToan(x_center, y_center)

#             if mqtt_client.is_connected():
#               print("Sending data to MQTT...")
#               mqtt_client.publish("dieukhienbom", json.dumps(data))
              
#               # Reset thời gian sau khi gửi
#               fire_detected_start_time = None
#             else:
#               print("MQTT client not connected.")

#     except Exception as e:
#       print("Error reading image:", e)




def TinhToan(x: float, y: float):  # x, y là tọa độ đã chuẩn hóa
    # const
    hCamera = 30   # chiều cao của camera so với mặt đất - cm
    d = 23.0       # chiều dài của góc nhìn của camera - cm
    r = 18.0       # chiều rộng của góc nhìn của camera - cm
    hServo = 28    # chiều cao của servo2 so với mặt đất - cm
    y1 = 1         # hình chiếu của servo2 xuống mặt đất - đã chuẩn hóa
    hNen = 6       # chiều cao cây nến muốn đạt được

    # góc 1 - góc quay của servo 1
    angle1 = 90  # angle1 là góc quay của servo1
    # mặc định là ban đầu 90 độ
    # thẳng đứng so với mặt đất
    alpha_radian = math.atan(abs(0.5 - x) * r / hCamera)  # góc theo radian
    alpha_degree = math.degrees(alpha_radian)             # góc theo độ

    # nếu hình chiếu của x lên mặt phẳng mà quá 0.5 thì góc > 90 độ
    if x < 0.5:
        angle1 += alpha_degree
    else:
        angle1 -= alpha_degree

    # góc 2 - góc quay của servo 2
    angle2 = 90
    # khoảng cách thực tế từ điểm cháy đến chân hình chiếu
    deltaY = (y1 - y) * d
    ch = math.sqrt(hServo ** 2 + deltaY ** 2)  # cạnh huyền của tam giác
    # góc quay alpha là góc quay với lửa ở vị trí đó, cao = 0cm
    alpha_radian = math.atan(deltaY / hServo)
    alpha_degree = math.degrees(alpha_radian)
    c = math.sqrt(hNen ** 2 + ch ** 2 - 2 * hNen * hServo)
    # góc quay beta là góc quay với lửa ở độ cao hNen
    beta_radian = math.acos((ch ** 2 + c ** 2 - hNen ** 2)/(2 * ch * c))
    beta_degree = math.degrees(beta_radian)

    # góc nhỏ hơn là góc 90 - alpha - beta
    angle2From = angle2 - alpha_degree - beta_degree

    # góc lớn hơn là góc 90 - alpha
    angle2To = angle2 - alpha_degree

    return {
      "goc1": int(angle1),
      "goc2From": int(angle2From),
      "goc2To": int(angle2To)
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
