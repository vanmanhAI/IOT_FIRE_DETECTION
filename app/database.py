from pymongo import MongoClient
from datetime import datetime

client = MongoClient('mongodb+srv://cvm:12345@twitter.7eviwvh.mongodb.net/')
db = client['FIRE_DETECTION']  
collection = db['fireNotifications'] 

def save_data(smoke, fire, light, image):
    data = {
        'smoke': smoke,
        'fire': fire,
        'light': light,
        'image': image,  # Có thể là đường dẫn tới ảnh hoặc dữ liệu ảnh
        'date': datetime.now()
    }
    collection.insert_one(data)
    
# test save_data
save_data(0, 1, 100, "image.jpg")