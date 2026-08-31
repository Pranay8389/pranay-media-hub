import os
import requests
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

# GitHub Config
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "") # Optional: Add in Render Environment Variables if needed
REPO_OWNER = "Pranay8389"
REPO_NAME = "pranay-media-hub"

FOLDERS = {
    "images": "images",
    "videos": "videos",
    "music": "mp3",
    "documents": "documents"
}

# Ensure local directories exist for temporary storage
for folder in FOLDERS.values():
    os.makedirs(folder, exist_ok=True)

def fetch_github_files(folder_path):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{folder_path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        files = response.json()
        return [file['download_url'] for file in files if file['type'] == 'file']
    return []

@app.route('/images', methods=['GET'])
def get_images():
    return jsonify(fetch_github_files(FOLDERS["images"]))

@app.route('/videos', methods=['GET'])
def get_videos():
    return jsonify(fetch_github_files(FOLDERS["videos"]))

@app.route('/music', methods=['GET'])
def get_music():
    return jsonify(fetch_github_files(FOLDERS["music"]))

@app.route('/documents', methods=['GET'])
def get_documents():
    return jsonify(fetch_github_files(FOLDERS["documents"]))

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    file_type = request.form.get('file_type', 'images')
    folder = FOLDERS.get(file_type, 'images')
    
    file_path = os.path.join(folder, file.filename)
    file.save(file_path)
    
    return jsonify({"message": "File uploaded successfully", "path": file_path}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
