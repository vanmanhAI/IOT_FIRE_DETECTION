from flask import Blueprint, Response
from app.utils import get_image_stream_client

main_bp = Blueprint('main', __name__)

@main_bp.route('/stream')
def index():
    return Response(get_image_stream_client(), mimetype='multipart/x-mixed-replace; boundary=frame')
