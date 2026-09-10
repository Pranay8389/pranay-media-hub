import os
import secrets

from flask import Flask, request, jsonify
from flask_cors import CORS

import cloudinary
import cloudinary.uploader

import psycopg2
from psycopg2.extras import RealDictCursor

from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
CORS(app)


# ============================================================
# ENVIRONMENT VARIABLES
# ============================================================

DATABASE_URL = os.environ.get("DATABASE_URL")

CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.environ.get("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET")


# ============================================================
# CLOUDINARY CONFIG
# ============================================================

cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
    secure=True
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_db_connection():
    if not DATABASE_URL:
        raise Exception("DATABASE_URL is not configured")

    return psycopg2.connect(DATABASE_URL)


# ============================================================
# CREATE DATABASE TABLES
# ============================================================

def init_database():

    conn = get_db_connection()

    try:
        cur = conn.cursor()

        # USERS TABLE
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL,
                email VARCHAR(255) UNIQUE,
                mobile VARCHAR(30) UNIQUE,
                username VARCHAR(100) UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE
                    DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # SESSIONS TABLE
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL
                    REFERENCES users(id)
                    ON DELETE CASCADE,
                token TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE
                    DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # FILES TABLE
        cur.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL
                    REFERENCES users(id)
                    ON DELETE CASCADE,
                filename TEXT,
                file_type VARCHAR(50) NOT NULL,
                cloudinary_public_id TEXT,
                url TEXT NOT NULL,
                resource_type VARCHAR(30),
                created_at TIMESTAMP WITH TIME ZONE
                    DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        cur.close()

    finally:
        conn.close()


# ============================================================
# AUTHENTICATION HELPER
# ============================================================

def get_current_user():

    auth_header = request.headers.get("Authorization", "")

    if not auth_header.startswith("Bearer "):
        return None

    token = auth_header.replace("Bearer ", "", 1).strip()

    if not token:
        return None

    conn = get_db_connection()

    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            SELECT users.*
            FROM users
            JOIN sessions
                ON users.id = sessions.user_id
            WHERE sessions.token = %s
        """, (token,))

        user = cur.fetchone()

        cur.close()

        return user

    finally:
        conn.close()


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    return jsonify({
        "status": "Pranay Media Hub Active",
        "authentication": "enabled"
    })


# ============================================================
# SIGNUP
# ============================================================

@app.route("/signup", methods=["POST"])
def signup():

    try:

        data = request.get_json() or {}

        first_name = data.get("first_name", "").strip()
        last_name = data.get("last_name", "").strip()
        email = data.get("email", "").strip().lower()
        mobile = data.get("mobile", "").strip()
        username = data.get("username", "").strip()
        password = data.get("password", "")

        # Required fields
        if not first_name:
            return jsonify({
                "error": "First name is required"
            }), 400

        if not last_name:
            return jsonify({
                "error": "Last name is required"
            }), 400

        if not email and not mobile:
            return jsonify({
                "error": "Email or mobile number is required"
            }), 400

        if not username:
            return jsonify({
                "error": "Username is required"
            }), 400

        if len(password) < 6:
            return jsonify({
                "error": "Password must contain at least 6 characters"
            }), 400

        # Empty values become NULL
        email = email if email else None
        mobile = mobile if mobile else None

        conn = get_db_connection()

        try:

            cur = conn.cursor(cursor_factory=RealDictCursor)

            # Check username
            cur.execute(
                "SELECT id FROM users WHERE username = %s",
                (username,)
            )

            if cur.fetchone():
                return jsonify({
                    "error": "Username already exists"
                }), 409

            # Check email
            if email:

                cur.execute(
                    "SELECT id FROM users WHERE email = %s",
                    (email,)
                )

                if cur.fetchone():
                    return jsonify({
                        "error": "Email already registered"
                    }), 409

            # Check mobile
            if mobile:

                cur.execute(
                    "SELECT id FROM users WHERE mobile = %s",
                    (mobile,)
                )

                if cur.fetchone():
                    return jsonify({
                        "error": "Mobile number already registered"
                    }), 409

            # Hash password
            password_hash = generate_password_hash(password)

            # Create user
            cur.execute("""
                INSERT INTO users (
                    first_name,
                    last_name,
                    email,
                    mobile,
                    username,
                    password_hash
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                first_name,
                last_name,
                email,
                mobile,
                username,
                password_hash
            ))

            user_id = cur.fetchone()["id"]

            conn.commit()

            return jsonify({
                "message": "Account created successfully",
                "user_id": user_id,
                "username": username
            }), 201

        finally:
            conn.close()

    except Exception as e:

        print("SIGNUP ERROR:", repr(e), flush=True)

        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# LOGIN
# ============================================================

@app.route("/login", methods=["POST"])
def login():

    try:

        data = request.get_json() or {}

        login_value = data.get("login", "").strip()
        password = data.get("password", "")

        if not login_value:
            return jsonify({
                "error": "Email, mobile number or username is required"
            }), 400

        if not password:
            return jsonify({
                "error": "Password is required"
            }), 400

        conn = get_db_connection()

        try:

            cur = conn.cursor(cursor_factory=RealDictCursor)

            cur.execute("""
                SELECT *
                FROM users
                WHERE
                    LOWER(username) = LOWER(%s)
                    OR LOWER(email) = LOWER(%s)
                    OR mobile = %s
                LIMIT 1
            """, (
                login_value,
                login_value,
                login_value
            ))

            user = cur.fetchone()

            if not user:
                return jsonify({
                    "error": "Invalid login details"
                }), 401

            if not check_password_hash(
                user["password_hash"],
                password
            ):
                return jsonify({
                    "error": "Invalid login details"
                }), 401

            # Create secure session token
            token = secrets.token_urlsafe(48)

            cur.execute("""
                INSERT INTO sessions (
                    user_id,
                    token
                )
                VALUES (%s, %s)
            """, (
                user["id"],
                token
            ))

            conn.commit()

            return jsonify({
                "message": "Login successful",
                "token": token,
                "user": {
                    "id": user["id"],
                    "first_name": user["first_name"],
                    "last_name": user["last_name"],
                    "email": user["email"],
                    "mobile": user["mobile"],
                    "username": user["username"]
                }
            }), 200

        finally:
            conn.close()

    except Exception as e:

        print("LOGIN ERROR:", repr(e), flush=True)

        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# CURRENT USER
# ============================================================

@app.route("/me", methods=["GET"])
def me():

    try:

        user = get_current_user()

        if not user:
            return jsonify({
                "error": "Unauthorized"
            }), 401

        return jsonify({
            "user": {
                "id": user["id"],
                "first_name": user["first_name"],
                "last_name": user["last_name"],
                "email": user["email"],
                "mobile": user["mobile"],
                "username": user["username"]
            }
        })

    except Exception as e:

        print("ME ERROR:", repr(e), flush=True)

        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout", methods=["POST"])
def logout():

    try:

        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return jsonify({
                "message": "Already logged out"
            })

        token = auth_header.replace("Bearer ", "", 1).strip()

        conn = get_db_connection()

        try:

            cur = conn.cursor()

            cur.execute(
                "DELETE FROM sessions WHERE token = %s",
                (token,)
            )

            conn.commit()

            cur.close()

            return jsonify({
                "message": "Logged out successfully"
            })

        finally:
            conn.close()

    except Exception as e:

        print("LOGOUT ERROR:", repr(e), flush=True)

        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# UPLOAD
# ============================================================

@app.route("/upload", methods=["POST"])
def upload_file():

    try:

        # ----------------------------------------------------
        # CHECK LOGIN
        # ----------------------------------------------------

        user = get_current_user()

        if not user:
            return jsonify({
                "error": "Please login first"
            }), 401

        # ----------------------------------------------------
        # CHECK FILE
        # ----------------------------------------------------

        if "file" not in request.files:
            return jsonify({
                "error": "No file uploaded"
            }), 400

        file = request.files["file"]

        if not file or not file.filename:
            return jsonify({
                "error": "Selected file is empty"
            }), 400

        # ----------------------------------------------------
        # FILE TYPE
        # ----------------------------------------------------

        file_type = request.form.get(
            "file_type",
            "images"
        ).strip().lower()

        allowed_types = [
            "images",
            "videos",
            "music",
            "documents"
        ]

        if file_type not in allowed_types:
            return jsonify({
                "error": "Invalid file type"
            }), 400

        # ----------------------------------------------------
        # CLOUDINARY RESOURCE TYPE
        # ----------------------------------------------------

        if file_type == "images":
            resource_type = "image"

        elif file_type in ["videos", "music"]:
            resource_type = "video"

        else:
            resource_type = "raw"

        # ----------------------------------------------------
        # USER-SPECIFIC CLOUDINARY FOLDER
        # ----------------------------------------------------

        folder = (
            f"pranay_media_hub/"
            f"users/"
            f"user_{user['id']}/"
            f"{file_type}"
        )

        print(
            "UPLOAD START:",
            {
                "user_id": user["id"],
                "filename": file.filename,
                "file_type": file_type,
                "resource_type": resource_type,
                "folder": folder
            },
            flush=True
        )

        # ----------------------------------------------------
        # UPLOAD TO CLOUDINARY
        # ----------------------------------------------------

        upload_result = cloudinary.uploader.upload(
            file,
            folder=folder,
            resource_type=resource_type
        )

        # ----------------------------------------------------
        # GET CLOUDINARY DATA
        # ----------------------------------------------------

        url = upload_result.get("secure_url")

        public_id = upload_result.get("public_id")

        if not url:
            raise Exception(
                "Cloudinary did not return secure_url"
            )

        # ----------------------------------------------------
        # SAVE FILE INFORMATION IN DATABASE
        # ----------------------------------------------------

        conn = get_db_connection()

        try:

            cur = conn.cursor()

            cur.execute("""
                INSERT INTO files (
                    user_id,
                    filename,
                    file_type,
                    cloudinary_public_id,
                    url,
                    resource_type
                )
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                user["id"],
                file.filename,
                file_type,
                public_id,
                url,
                resource_type
            ))

            conn.commit()

            cur.close()

        finally:
            conn.close()

        print(
            "UPLOAD SUCCESS:",
            {
                "user_id": user["id"],
                "filename": file.filename,
                "url": url
            },
            flush=True
        )

        # ----------------------------------------------------
        # RESPONSE
        # ----------------------------------------------------

        return jsonify({
            "message": "Uploaded successfully",
            "url": url,
            "file_type": file_type,
            "user_id": user["id"]
        }), 200

    except Exception as e:

        # IMPORTANT:
        # This prints the real upload error in Render logs.
        print(
            "UPLOAD ERROR:",
            repr(e),
            flush=True
        )

        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# GET USER FILES
# ============================================================

def get_user_files(file_type):

    try:

        # ----------------------------------------------------
        # CHECK LOGIN
        # ----------------------------------------------------

        user = get_current_user()

        if not user:
            return jsonify({
                "error": "Please login first"
            }), 401

        # ----------------------------------------------------
        # DATABASE
        # ----------------------------------------------------

        conn = get_db_connection()

        try:

            cur = conn.cursor(
                cursor_factory=RealDictCursor
            )

            cur.execute("""
                SELECT
                    id,
                    filename,
                    file_type,
                    cloudinary_public_id,
                    url,
                    resource_type,
                    created_at
                FROM files
                WHERE user_id = %s
                AND file_type = %s
                ORDER BY created_at DESC
            """, (
                user["id"],
                file_type
            ))

            files = cur.fetchall()

            cur.close()

            return jsonify([
                {
                    "id": f["id"],
                    "filename": f["filename"],
                    "url": f["url"],
                    "file_type": f["file_type"],
                    "cloudinary_public_id":
                        f["cloudinary_public_id"],
                    "resource_type":
                        f["resource_type"]
                }
                for f in files
            ])

        finally:
            conn.close()

    except Exception as e:

        print(
            "GET FILES ERROR:",
            repr(e),
            flush=True
        )

        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# IMAGES
# ============================================================

@app.route("/images", methods=["GET"])
def get_images():

    return get_user_files("images")


# ============================================================
# VIDEOS
# ============================================================

@app.route("/videos", methods=["GET"])
def get_videos():

    return get_user_files("videos")


# ============================================================
# MUSIC
# ============================================================

@app.route("/music", methods=["GET"])
def get_music():

    return get_user_files("music")


# ============================================================
# DOCUMENTS
# ============================================================

@app.route("/documents", methods=["GET"])
def get_documents():

    return get_user_files("documents")


# ============================================================
# STARTUP
# ============================================================

try:

    init_database()

    print(
        "DATABASE INITIALIZATION SUCCESS",
        flush=True
    )

except Exception as e:

    print(
        "DATABASE INITIALIZATION ERROR:",
        repr(e),
        flush=True
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(
            os.environ.get(
                "PORT",
                5000
            )
        )
    )
