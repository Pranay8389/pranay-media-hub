import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Cloudinary Library
import cloudinary
import cloudinary.uploader
import cloudinary.api

load_dotenv()

app = Flask(__name__)

# ====================================================
# 🟢 CLOUDINARY CONFIGURATION
# మీ వివరాలతో ఇక్కడ రీప్లేస్ చేయండి
# ====================================================
cloudinary.config( 
  cloud_name = "మీ_CLOUD_NAME",      # <--- ఇక్కడ మార్చండి
  api_key = "మీ_API_KEY",            # <--- ఇక్కడ మార్చండి
  api_secret = "మీ_API_SECRET",      # <--- ఇక్కడ మార్చండి
  secure = True
)

@app.route('/upload', methods=['POST'])
def upload_media():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
            
        file = request.files['file']
        file_type = request.form.get('file_type', 'images')

        if file.filename == '':
            return jsonify({"error": "No filename selected"}), 400

        upload_result = cloudinary.uploader.upload(
            file, 
            resource_type="auto", 
            folder=f"pranay_media_hub/{file_type}",
            use_filename=True,
            unique_filename=True
        )

        secure_url = upload_result.get('secure_url')

        return jsonify({
            "message": "Media uploaded successfully to Cloud",
            "url": secure_url,
            "file_type": file_type
        }), 200

    except Exception as e:
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500

@app.route('/images', methods=['GET'])
def get_images():
    try:
        result = cloudinary.api.resources(
            type="upload",
            prefix="pranay_media_hub/images",
            resource_type="image",
            max_results=100
        )
        urls = [res['secure_url'] for res in result['resources']]
        return jsonify(urls)
    except Exception as e:
        return jsonify([])

@app.route('/videos', methods=['GET'])
def get_videos():
    try:
        result = cloudinary.api.resources(
            type="upload",
            prefix="pranay_media_hub/videos",
            resource_type="video",
            max_results=100
        )
        urls = [res['secure_url'] for res in result['resources']]
        return jsonify(urls)
    except Exception as e:
        return jsonify([])

@app.route('/music', methods=['GET'])
def get_music():
    try:
        result = cloudinary.api.resources(
            type="upload",
            prefix="pranay_media_hub/music",
            resource_type="raw",
            max_results=100
        )
        urls = [res['secure_url'] for res in result['resources']]
        return jsonify(urls)
    except Exception as e:
        return jsonify([])

@app.route('/documents', methods=['GET'])
def get_documents():
    try:
        result = cloudinary.api.resources(
            type="upload",
            prefix="pranay_media_hub/documents",
            resource_type="raw",
            max_results=100
        )
        urls = [res['secure_url'] for res in result['resources']]
        return jsonify(urls)
    except Exception as e:
        return jsonify([])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
