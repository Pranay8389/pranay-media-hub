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

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['file']
        file_type = request.form.get('file_type', 'images')

        resource_type = "auto"
        if file_type in ['images']:
            resource_type = "image"
        elif file_type in ['videos', 'music']:
            resource_type = "video"
        elif file_type in ['documents']:
            resource_type = "raw"

        upload_result = cloudinary.uploader.upload(
            file,
            folder = f"pranay_media_hub/{file_type}",
            resource_type = resource_type
        )

        return jsonify({
            "message": "Uploaded successfully",
            "url": upload_result.get('secure_url')
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_cloudinary_resources(folder_name, resource_type="image"):
    try:
        # Search both with and without trailing slash to guarantee fetch
        resources = cloudinary.api.resources(
            type = "upload",
            prefix = f"pranay_media_hub/{folder_name}",
            resource_type = resource_type,
            max_results = 500
        )
        return [res['secure_url'] for res in resources.get('resources', [])]
    except Exception as e:
        print(f"Error fetching {folder_name}: {e}")
        return []

@app.route('/images', methods=['GET'])
def get_images():
    return jsonify(get_cloudinary_resources('images', 'image'))

@app.route('/videos', methods=['GET'])
def get_videos():
    return jsonify(get_cloudinary_resources('videos', 'video'))

@app.route('/music', methods=['GET'])
def get_music():
    return jsonify(get_cloudinary_resources('music', 'video'))

@app.route('/documents', methods=['GET'])
def get_documents():
    return jsonify(get_cloudinary_resources('documents', 'raw'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
