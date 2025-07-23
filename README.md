# Online-Class-Attentiveness-Detector
# 🧠 EduPulse – Real-Time Online Class Attentiveness Detector

**EduPulse** is a smart, webcam-based AI tool designed to monitor and record student attentiveness during online classes in real-time. The system leverages facial landmark tracking and head pose estimation to detect eye closure and gaze direction, logging moments of distraction directly into a database. No external hardware or sensors are required — only a webcam and browser.

---

## 🎯 Objective

To help educators track and improve student engagement during virtual learning by providing a non-intrusive, real-time attentiveness monitoring solution.

---

## ⚙️ Technologies Used

| Layer          | Tools & Libraries                          |
|----------------|--------------------------------------------|
| Language       | Python, HTML, CSS, JavaScript              |
| CV/NLP         | OpenCV, MediaPipe                          |
| Web Framework  | Flask                                      |
| Frontend       | HTML, CSS (Bootstrap)                      |
| Backend Logic  | Head Pose Estimation, Eye Aspect Ratio     |
| Database       | SQLite + SQLAlchemy (optional ORM)         |

---

## 🔁 Functional Workflow

1. **Webcam Feed** → Captured via OpenCV  
2. **FaceMesh (MediaPipe)** → Extracts 468 facial landmarks  
3. **EAR & Gaze Logic** → Determines attention state  
4. **Head Pose Estimation** → Identifies direction of gaze  
5. **Attention Logging** → Data saved in real-time to SQLite  
6. **Web Interface (Flask)** → Displays alerts and insights

---

## 🗃️ Database Integration

EduPulse includes a built-in SQLite database to store all inattentive events:

| Field         | Description                              |
|---------------|------------------------------------------|
| `id`          | Auto-incremented ID                      |
| `student_id`  | Unique student/session identifier        |
| `timestamp`   | Date & time of inattention               |
| `status`      | Attention state (`Distracted`, `Focused`)|
| `duration`    | (Optional) Inattention duration in sec   |

> Stored using **SQLite**. Easily upgradable to MySQL/PostgreSQL.

---


---

## 🧪 Sample Visuals

### 🎯 Focus Detected  
![Focus](focus_detected.png)

### 😴 Not Paying Attention  
![Distracted](not_paying_attention.png)

---

## 🚀 How to Run

```bash
git clone https://github.com/your-username/edupulse-attention-detector
cd edupulse-attention-detector
pip install -r requirements.txt
python src/app.py


