from pymongo import MongoClient, DESCENDING, ASCENDING
from datetime import datetime

client = MongoClient('mongodb+srv://cvm:12345@twitter.7eviwvh.mongodb.net/')
db = client['FIRE_DETECTION']  
historyFireCollection = db['historyFire']   # Lịch sử các vụ cháy 
logCollection = db['logs']  # Lịch sử các hoạt động của hệ thống

# Tạo chỉ mục trên trường 'date' để sắp xếp nhanh
historyFireCollection.create_index([("date", DESCENDING)])
    
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
    
    # Kiểm tra số lượng bản ghi
    count = historyFireCollection.count_documents({})
    if count > 100:
        # Tìm các bản ghi cũ nhất cần xóa
        old_docs = historyFireCollection.find().sort("date", ASCENDING).limit(count - 100)
        old_ids = [doc['_id'] for doc in old_docs]
        if old_ids:
            historyFireCollection.delete_many({'_id': {'$in': old_ids}})

def save_log(oldState, newState):
    data = {
        'oldState': oldState,
        'newState': newState,
        'date': datetime.now()
    }
    logCollection.insert_one(data)

# test save_history_fire_data
# save_history_fire_data(100, 200, 300, 400, 50, 100)
# test save_log
# save_log("safe", "safe")