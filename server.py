import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Cloudinary Library ఇక్కడ Import చేయాలి
import cloudinary
import cloudinary.uploader
import cloudinary.api

# .env ఫైల్ లోని Variables లోడ్ చేయడానికి
load_dotenv()

app = Flask(__name__)

#====================================================
# 🟢 STEP 1: CLOUDINARY CONFIGURATION (తప్పనిసరి)
# మీ Cloudinary Dashboard నుండి ఈ వివరాలు తీసుకోండి
#====================================================
cloudinary.config( 
  cloud_name = "మీ_CLOUD_NAME",      # <--- ఇక్కడ మార్చండి
  api_key = "మీ_API_KEY",            # <--- ఇక్కడ మార్చండి
  api_secret = "మీ_API_SECRET",      # <--- ఇక్కడ మార్చండి
  secure = True
)

# Render లో Persistence లేని ఫోల్డర్లు వాడకూడదు.
# Cloudinary వాడుతున్నాం కాబట్టి Local folders అవసరం లేదు.

@app.route('/upload', methods=['POST'])
def upload_media():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
            
        file = request.files['file']
        file_type = request.form.get('file_type', 'images') # android 'images', 'videos' అని పంపుతుంది

        if file.filename == '':
            return jsonify({"error": "No filename selected"}), 400

        #========================================================
        # 🟢 STEP 2: DYNAMIC CLOUDINARY UPLOAD (MAIN FIX)
        # ఫైల్ ని డైరెక్ట్ గా Cloudinary కి అప్‌లోడ్ చేస్తాం
        #========================================================
        # resource_type 'auto' అంటే image/video ని ఆటోమేటిక్ గా గుర్తిస్తుంది
        upload_result = cloudinary.uploader.upload(
            file, 
            resource_type="auto", 
            folder=f"pranay_media_hub/{file_type}",
            use_filename=True,
            unique_filename=True
        )

        # Cloudinary నుండి వచ్చిన Secure URL
        secure_url = upload_result.get('secure_url')

        print(f"Uploaded Successfully to Cloudinary: {secure_url}")

        return jsonify({
            "message": "Media uploaded successfully to Cloud",
            "url": secure_url,
            "file_type": file_type
        }), 200

    except Exception as e:
        print(f"Error during upload: {str(e)}")
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500

@app.route('/images', methods=['GET'])
def get_images():
    try:
        # Cloudinary నుండి Images లిస్ట్ తెచ్చుకోవడం
        result = cloudinary.api.resources(
            type="upload",
            prefix="pranay_media_hub/images", # Folder path
            resource_type="image",
            max_results=100
        )
        # కేవలం Secure URLs ని మాత్రమే Android కి పంపడం
        urls = [res['secure_url'] for res in result['resources']]
        return jsonify(urls)
    except Exception as e:
        return jsonify([])

@app.route('/videos', methods=['GET'])
def get_videos():
    try:
        # Cloudinary నుండి Videos లిస్ట్ తెచ్చుకోవడం
        result = cloudinary.api.resources(
            type="upload",
            prefix="pranay_media_hub/videos", # Folder path
            resource_type="video",
            max_results=100
        )
        # Secure URLs for videos
        urls = [res['secure_url'] for res in result['resources']]
        return jsonify(urls)
    except Exception as e:
        return jsonify([])

@app.route('/music', methods=['GET'])
def get_music():
    # Music కోసం కూడా resource_type="raw" వాడాలి
    try:
        result = cloudinary.api.resources(
            type="upload",
            prefix="pranay_media_hub/music",
            resource_type="raw", # Music files are considered raw in Cloudinary
            max_results=100
        )
        urls = [res['secure_url'] for res in result['resources']]
        return jsonify(urls)
    except Exception as e:
        return jsonify([])

@app.route('/documents', methods=['GET'])
def get_documents():
    # Documents resource_type="raw"
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
