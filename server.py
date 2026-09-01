import os
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

# Render లో Persistent Storage వాడటానికి Base Path
BASE_DIR = os.getenv('RENDER_DISK_PATH', os.getcwd())
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

# ఫోల్డర్లు లేకపోతే క్రియేట్ చేయడం
os.makedirs(os.path.join(UPLOAD_FOLDER, 'images'), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'videos'), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'music'), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'documents'), exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
            
        file = request.files['file']
        file_type = request.form.get('file_type', 'documents')

        if file.filename == '':
            return jsonify({"error": "No filename provided"}), 400

        valid_folders = ['images', 'videos', 'music', 'documents']
        if file_type not in valid_folders:
            file_type = 'documents'

        save_dir = os.path.join(UPLOAD_FOLDER, file_type)
        save_path = os.path.join(save_dir, file.filename)
        
        file.save(save_path)

        return jsonify({"message": "File uploaded successfully", "path": f"/uploads/{file_type}/{file.filename}"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/images', methods=['GET'])
def get_images():
    path = os.path.join(UPLOAD_FOLDER, 'images')
    files = os.listdir(path) if os.path.exists(path) else []
    return jsonify([f"/uploads/images/{f}" for f in files])

@app.route('/videos', methods=['GET'])
def get_videos():
    path = os.path.join(UPLOAD_FOLDER, 'videos')
    files = os.listdir(path) if os.path.exists(path) else []
    return jsonify([f"/uploads/videos/{f}" for f in files])

@app.route('/music', methods=['GET'])
def get_music():
    path = os.path.join(UPLOAD_FOLDER, 'music')
    files = os.listdir(path) if os.path.exists(path) else []
    return jsonify([f"/uploads/music/{f}" for f in files])

@app.route('/documents', methods=['GET'])
def get_documents():
    path = os.path.join(UPLOAD_FOLDER, 'documents')
    files = os.listdir(path) if os.path.exists(path) else []
    return jsonify([f"/uploads/documents/{f}" for f in files])

@app.route('/uploads/<folder>/<filename>', methods=['GET'])
def serve_file(folder, filename):
    return send_from_directory(os.path.join(UPLOAD_FOLDER, folder), filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
