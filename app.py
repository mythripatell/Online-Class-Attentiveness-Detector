from flask import Flask, render_template, request, redirect, url_for, session, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import cv2
import mediapipe as mp
import numpy as np
from datetime import datetime
import os

# ---------------- HEADLESS SETTINGS ---------------- #
os.environ["DISPLAY"] = ":0"  # Prevent GUI errors on Render
LOCAL = os.environ.get("LOCAL", "1") == "1"  # Local webcam if LOCAL=1

# ---------------- FLASK SETUP ---------------- #
app = Flask(__name__)
app.secret_key = "supersecret123"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ---------------- DATABASE MODEL ---------------- #
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# ---------------- FACE TRACKING SETUP ---------------- #
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)
mp_drawing = mp.solutions.drawing_utils

EAR_THRESHOLD = 0.15
FACE_POINTS = [1, 33, 263, 61, 291, 199]
LEFT_EYE_IDX = [362, 385, 387, 263, 373, 380]
RIGHT_EYE_IDX = [33, 160, 158, 133, 153, 144]

model_points = np.array([
    [0.0, 0.0, 0.0],
    [-30.0, -125.0, -30.0],
    [30.0, -125.0, -30.0],
    [-70.0, -60.0, -50.0],
    [70.0, -60.0, -50.0],
    [0.0, -150.0, -10.0]
], dtype=np.float64)

# Conditional webcam setup
camera = cv2.VideoCapture(0) if LOCAL else None
inattention_log = []

def calculate_ear(eye_points):
    A = np.linalg.norm(eye_points[1] - eye_points[5])
    B = np.linalg.norm(eye_points[2] - eye_points[4])
    C = np.linalg.norm(eye_points[0] - eye_points[3])
    return (A + B) / (2.0 * C)

# ---------------- VIDEO STREAM LOGIC ---------------- #
def generate_frames():
    while True:
        if LOCAL:
            success, frame = camera.read()
            if not success:
                break
        else:
            # On Render, no webcam: generate blank frame or skip
            frame = np.zeros((480, 640, 3), dtype=np.uint8)

        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)

        attention = "No Face Detected"
        color = (0, 0, 255)

        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0]
            landmarks = face_landmarks.landmark
            left_eye = np.array([[landmarks[i].x * w, landmarks[i].y * h] for i in LEFT_EYE_IDX])
            right_eye = np.array([[landmarks[i].x * w, landmarks[i].y * h] for i in RIGHT_EYE_IDX])
            left_ear = calculate_ear(left_eye)
            right_ear = calculate_ear(right_eye)
            avg_ear = (left_ear + right_ear) / 2.0

            image_points = np.array([[landmarks[i].x * w, landmarks[i].y * h] for i in FACE_POINTS], dtype=np.float64)
            focal_length = w
            center = (w / 2, h / 2)
            camera_matrix = np.array([[focal_length, 0, center[0]],
                                      [0, focal_length, center[1]],
                                      [0, 0, 1]], dtype="double")
            dist_coeffs = np.zeros((4, 1))

            success_pnp, rot_vec, trans_vec = cv2.solvePnP(model_points, image_points, camera_matrix, dist_coeffs)

            if success_pnp:
                rmat, _ = cv2.Rodrigues(rot_vec)
                pose_mat = cv2.hconcat((rmat, trans_vec))
                _, _, _, _, _, _, euler_angles = cv2.decomposeProjectionMatrix(pose_mat)
                yaw = euler_angles[1][0]
                pitch = euler_angles[0][0]

                if -75 <= yaw <= 75 and -95 <= pitch <= 95 and avg_ear > EAR_THRESHOLD:
                    attention = "Paying Attention"
                    color = (0, 255, 0)
                else:
                    attention = "Not Paying Attention"
                    color = (0, 0, 255)
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    inattention_log.append({
                        "timestamp": timestamp,
                        "yaw": int(yaw),
                        "pitch": int(pitch),
                        "ear": round(avg_ear, 2)
                    })

                cv2.putText(frame, f"Yaw: {int(yaw)} Pitch: {int(pitch)} EAR: {avg_ear:.2f}", 
                            (10, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            mp_drawing.draw_landmarks(
                frame, face_landmarks, mp_face_mesh.FACEMESH_CONTOURS,
                mp_drawing.DrawingSpec(color=color, thickness=1, circle_radius=1),
                mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=1)
            )

        cv2.putText(frame, attention, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

# ---------------- ROUTES ---------------- #
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/edu')
def edu():
    return render_template('edu.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('edu'))  
        else:
            error = "Invalid username or password"
    return render_template('login.html', error=error)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing = User.query.filter_by(username=username).first()
        if existing:
            return "Username already exists!"
        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/inattention_data')
def inattention_data():
    return jsonify(inattention_log)

# ---------------- START SERVER ---------------- #
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)  # debug=False for Render
