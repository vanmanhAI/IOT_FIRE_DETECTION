# DATABASE.PY

from pymongo import MongoClient
from datetime import datetime

client = MongoClient('mongodb+srv://cvm:12345@twitter.7eviwvh.mongodb.net/')
db = client['FIRE_DETECTION']  
collection_notifications = db['fireNotifications'] 
collection_status = db['fireStatus']  # Tạo bảng mới

def save_notification(smoke, fire, light, image):
    data = {
        'smoke': smoke,
        'fire': fire,
        'light': light,
        'image': image,  # Đường dẫn tới ảnh hoặc dữ liệu ảnh
        'date': datetime.now()
    }
    collection_notifications.insert_one(data)

def save_status(status, percentage):
    data = {
        'status': status,
        'percentage': percentage,
        'date': datetime.now()
    }
    collection_status.insert_one(data)
    
def get_latest_fire_status(limit=20):
    """
    Lấy 20 bản ghi mới nhất từ bảng fireStatus.
    """
    try:
        records = list(collection_status.find().sort('date', -1).limit(limit))
        for record in records:
            record['_id'] = str(record['_id'])  # Chuyển ObjectId thành chuỗi
            record['date'] = record['date'].strftime('%Y-%m-%d %H:%M:%S')  # Định dạng datetime
        return records
    except Exception as e:
        print(f"Error fetching latest fire status: {e}")
        return []
    
# Test save_data
save_notification(0, 1, 100, "image.jpg")
save_status("an toàn", 0)