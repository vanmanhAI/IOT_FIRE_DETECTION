from flask import Blueprint, jsonify, request, Response
from app.utils import get_image_stream_client
from app.database import get_latest_fire_status  # Import hàm lấy dữ liệu

main_bp = Blueprint('main', __name__)

@main_bp.route('/stream')
def stream():
    return Response(get_image_stream_client(), mimetype='multipart/x-mixed-replace; boundary=frame')

@main_bp.route('/fire-level', methods=['GET'])
def get_fire_level():
    """
    API Endpoint để lấy 20 bản ghi mới nhất từ bảng fireStatus.
    """
    try:
        latest_status = get_latest_fire_status(20)
        return jsonify(latest_status), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500