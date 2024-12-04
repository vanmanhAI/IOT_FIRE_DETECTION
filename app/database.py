from pymongo import MongoClient
from datetime import datetime

client = MongoClient('mongodb+srv://cvm:12345@twitter.7eviwvh.mongodb.net/')
db = client['FIRE_DETECTION']  
collection = db['fireNotifications']
historyFireCollection = db['historyFire']   # Lịch sử các vụ cháy 
logCollection = db['logs']  # Lịch sử các hoạt động của hệ thống

def save_data(smoke, fire, light, image):
    data = {
        'smoke': smoke,
        'fire': fire,
        'light': light,
        'image': image,  # Có thể là đường dẫn tới ảnh hoặc dữ liệu ảnh
        'date': datetime.now()
    }
    collection.insert_one(data)
    
    # LUA1, LUA2, LUA3, KHOI, %CHAY, %DETECT
def save_history_fire_data(lua1, lua2, lua3, khoi, chay, detect):
    # Tinh phan tram chay
    data = {
        'lua1': lua1,
        'lua2': lua2,
        'lua3': lua3,
        'khoi': khoi,
        'chay': chay,
        'detect': detect,
        'date': datetime.now()
    }
    historyFireCollection.insert_one(data)

def save_log(oldState, newState):
    data = {
        'oldState': oldState,
        'newState': newState,
        'date': datetime.now()
    }
    logCollection.insert_one(data)
    
# test save_data
save_data(0, 1, 100, "image.jpg")
# test save_history_fire_data
save_history_fire_data(100, 200, 300, 400, 50, 100)
# test save_log
save_log("safe", "safe")