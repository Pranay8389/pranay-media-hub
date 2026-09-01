import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import cloudinary
import cloudinary.uploader
import cloudinary.api

app = Flask(__name__)
CORS(app)

CLOUDINARY_CLOUD_NAME = "hs6ssya2"
CLOUDINARY_API_KEY = "829421843387563"
CLOUDINARY_API_SECRET = "6A20eVzCnAtsjd2WFWz3QokjxuY"

cloudinary.config(
    cloud_name = CLOUDINARY_CLOUD_NAME,
    api_key = CLOUDINARY_API_KEY,
    api_secret = CLOUDINARY_API_SECRET,
    secure = True
)

@app.route('/')
def home():
    return jsonify({"status": "Pranay Media Hub Active"})

# Optimized Universal Upload Endpoint
@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['file']
        filename = file.filename.lower()

        # Automatic Resource Type & Extension Mapping
        resource_type = "auto"
        folder_path = "pranay_media_hub/other"

        if filename.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
            resource_type = "image"
            folder_path = "pranay_media_hub/images"
        elif filename.endswith(('.mp4', '.mkv', '.mov', '.avi', '.webm', '.3gp')):
            resource_type = "video"
            folder_path = "pranay_media_hub/videos"
        elif filename.endswith(('.mp3', '.wav', '.m4a', '.aac', '.ogg', '.flac')):
            resource_type = "video"  # Cloudinary requires 'video' resource_type for Audio
            folder_path = "pranay_media_hub/music"
        elif filename.endswith(('.pdf', '.docx', '.txt', '.zip')):
            resource_type = "raw"
            folder_path = "pranay_media_hub/documents"

        # Using upload_large to handle both small and large media files securely
        upload_result = cloudinary.uploader.upload_large(
            file,
            folder = folder_path,
            resource_type = resource_type,
            chunk_size = 6000000  # 6MB Chunks
        )

        return jsonify({
            "message": "Uploaded successfully",
            "url": upload_result.get('secure_url')
        }), 200

    except Exception as e:
        print(f"Upload Error: {e}")
        return jsonify({"error": str(e)}), 500

# Fetch Endpoints
@app.route('/images', methods=['GET'])
def get_images():
    try:
        resources = cloudinary.api.resources(
            type = "upload", resource_type = "image", max_results = 500
        )
        return jsonify([res['secure_url'] for res in resources.get('resources', [])])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/videos', methods=['GET'])
def get_videos():
    try:
        resources = cloudinary.api.resources(
            type = "upload", resource_type = "video", max_results = 500
        )
        all_videos = resources.get('resources', [])
        video_urls = [
            res['secure_url'] for res in all_videos 
            if res.get('format') in ['mp4', 'mkv', 'mov', 'avi', 'webm', '3gp']
        ]
        return jsonify(video_urls)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/music', methods=['GET'])
def get_music():
    try:
        resources = cloudinary.api.resources(
            type = "upload", resource_type = "video", max_results = 500
        )
        all_media = resources.get('resources', [])
        music_urls = [
            res['secure_url'] for res in all_media 
            if res.get('format') in ['mp3', 'wav', 'm4a', 'aac', 'ogg', 'flac']
        ]
        return jsonify(music_urls)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/documents', methods=['GET'])
def get_documents():
    try:
        resources = cloudinary.api.resources(
            type = "upload", resource_type = "raw", max_results = 500
        )
        return jsonify([res['secure_url'] for res in resources.get('resources', [])])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
