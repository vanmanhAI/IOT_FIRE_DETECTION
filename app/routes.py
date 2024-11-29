from flask import Blueprint, jsonify, request, Response
from app.utils import get_image_stream_client

main_bp = Blueprint('main', __name__)

@main_bp.route('/stream')
def index():
    return Response(get_image_stream_client(), mimetype='multipart/x-mixed-replace; boundary=frame')

@main_bp.route('/fire-level', methods=['GET'])
def get_fire_level():
    pass

