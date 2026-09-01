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

# Strict Folder Filtering so files don't mix/duplicate
@app.route('/images', methods=['GET'])
def get_images():
    try:
        resources = cloudinary.api.resources(
            type = "upload",
            resource_type = "image",
            prefix = "pranay_media_hub/images",
            max_results = 500
        )
        return jsonify([res['secure_url'] for res in resources.get('resources', [])])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/videos', methods=['GET'])
def get_videos():
    try:
        resources = cloudinary.api.resources(
            type = "upload",
            resource_type = "video",
            prefix = "pranay_media_hub/videos",
            max_results = 500
        )
        return jsonify([res['secure_url'] for res in resources.get('resources', [])])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/music', methods=['GET'])
def get_music():
    try:
        resources = cloudinary.api.resources(
            type = "upload",
            resource_type = "video",
            prefix = "pranay_media_hub/music",
            max_results = 500
        )
        return jsonify([res['secure_url'] for res in resources.get('resources', [])])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/documents', methods=['GET'])
def get_documents():
    try:
        resources = cloudinary.api.resources(
            type = "upload",
            resource_type = "raw",
            prefix = "pranay_media_hub/documents",
            max_results = 500
        )
        return jsonify([res['secure_url'] for res in resources.get('resources', [])])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
