from flask import Flask, render_template, request, redirect, url_for, session, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin
import qrcode
import os
from io import BytesIO
from datetime import datetime
from reportlab.pdfgen import canvas
import pandas as pd
import matplotlib.pyplot as plt
import cv2
import numpy as np
from PIL import Image
from geopy.distance import geodesic

# ----------------------
# App Setup
# ----------------------
app = Flask(__name__)
app.secret_key = "secretkey123"

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'database')
if not os.path.exists(db_path):
    os.makedirs(db_path)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(db_path, 'attendance.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

# ----------------------
# Database Models
# ----------------------
class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    latitude = db.Column(db.Float)   # Admin-defined latitude
    longitude = db.Column(db.Float)  # Admin-defined longitude
    radius = db.Column(db.Float)     # Radius in meters

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    rating = db.Column(db.Integer)
    dropdown = db.Column(db.String(50))
    short_answer = db.Column(db.String(200))

# ----------------------
# Create tables & default admin
# ----------------------
with app.app_context():
    db.create_all()
    if not Admin.query.filter_by(username="admin").first():
        default_admin = Admin(username="admin", password="admin123")
        db.session.add(default_admin)
        db.session.commit()
        print("Default admin created: username=admin, password=admin123")

# ----------------------
# Login Manager
# ----------------------
@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

# ----------------------
# Routes
# ----------------------
@app.route("/")
def index():
    return render_template("index.html")

# Admin Login
@app.route("/admin_login", methods=["POST"])
def admin_login():
    username = request.form['username']
    password = request.form['password']
    admin = Admin.query.filter_by(username=username, password=password).first()
    if admin:
        login_user(admin)
        return redirect(url_for("admin_dashboard"))
    else:
        return "Invalid Credentials"

# Student Login (session-based)
@app.route("/student_login", methods=["POST"])
def student_login():
    email = request.form['email']
    student = Student.query.filter_by(email=email).first()
    if not student:
        student = Student(email=email)
        db.session.add(student)
        db.session.commit()
    session['student_id'] = student.id
    session['student_email'] = student.email
    return redirect(url_for("student_dashboard"))

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# ----------------------
# Admin Routes
# ----------------------
@app.route("/admin_dashboard")
@login_required
def admin_dashboard():
    events = Event.query.all()
    feedbacks = Feedback.query.all()
    
    attendance_chart_file = None
    feedback_chart_file = None

    # Attendance Analysis
    if events:
        event_stats = []
        for e in events:
            total_students = Student.query.count()
            attended = Attendance.query.filter_by(event_id=e.id).count()
            percentage = (attended / total_students * 100) if total_students > 0 else 0
            event_stats.append((e.name, attended, total_students, percentage))
        
        # Plot Attendance
        df_att = pd.DataFrame(event_stats, columns=["Event","Attended","Total Students","Percentage"])
        attendance_chart_file = os.path.join(basedir,"static","attendance_chart.png")
        df_att.plot(x="Event", y="Percentage", kind="bar", legend=False)
        plt.ylabel("Attendance %")
        plt.title("Event-wise Attendance")
        plt.savefig(attendance_chart_file)
        plt.close()

    # Feedback Analysis
    if feedbacks:
        df_fb = pd.DataFrame([(f.event_id, f.rating) for f in feedbacks], columns=["event_id","rating"])
        feedback_chart_file = os.path.join(basedir,"static","feedback_chart.png")
        df_fb.groupby("event_id").mean().plot(kind="bar", legend=False)
        plt.title("Average Rating per Event")
        plt.ylabel("Average Rating")
        plt.savefig(feedback_chart_file)
        plt.close()
    
    return render_template("admin_dashboard.html", events=events, 
                           attendance_chart_file=attendance_chart_file, 
                           feedback_chart_file=feedback_chart_file)

@app.route("/create_event", methods=["POST"])
@login_required
def create_event():
    name = request.form['name']
    latitude = float(request.form['latitude'])
    longitude = float(request.form['longitude'])
    radius = float(request.form['radius'])
    event = Event(name=name, latitude=latitude, longitude=longitude, radius=radius)
    db.session.add(event)
    db.session.commit()
    return redirect(url_for("admin_dashboard"))

@app.route("/generate_qr/<int:event_id>")
@login_required
def generate_qr(event_id):
    event = Event.query.get(event_id)
    if not event:
        return "Event not found!"
    qr_data = f"event_id:{event.id}"
    img = qrcode.make(qr_data)
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype='image/png', download_name=f"event_{event.id}_qr.png")

# ----------------------
# Student Routes
# ----------------------
@app.route("/student_dashboard")
def student_dashboard():
    if 'student_id' not in session:
        return redirect(url_for("index"))
    events = Event.query.all()
    return render_template("student_dashboard.html", events=events)

@app.route("/mark_attendance", methods=["POST"])
def mark_attendance():
    if 'student_id' not in session:
        return jsonify({"message":"Please login first!"})
    
    event_id = int(request.form['event_id'])
    file = request.files['qr_image']
    student_lat = float(request.form['latitude'])
    student_lon = float(request.form['longitude'])

    # Read QR image
    img = Image.open(file.stream)
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    
    detector = cv2.QRCodeDetector()
    data, bbox, _ = detector.detectAndDecode(img)
    
    if not data:
        return "Could not read QR code!"
    
    if data != f"event_id:{event_id}":
        return "Invalid QR content!"

    # GPS validation
    event = Event.query.get(event_id)
    event_loc = (event.latitude, event.longitude)
    student_loc = (student_lat, student_lon)
    distance = geodesic(event_loc, student_loc).meters

    if distance > event.radius:
        return f"You are out of the allowed radius! Distance: {int(distance)} meters"

    # Save attendance
    attendance = Attendance(student_id=session['student_id'], event_id=event_id)
    db.session.add(attendance)
    db.session.commit()
    
    return redirect(url_for("feedback_form", event_id=event_id))

@app.route("/feedback/<int:event_id>", methods=["GET","POST"])
def feedback_form(event_id):
    if 'student_id' not in session:
        return redirect(url_for("index"))
    if request.method=="POST":
        rating = int(request.form['rating'])
        dropdown = request.form['dropdown']
        short_answer = request.form['short_answer']
        feedback = Feedback(student_id=session['student_id'], event_id=event_id,
                            rating=rating, dropdown=dropdown, short_answer=short_answer)
        db.session.add(feedback)
        db.session.commit()
        return "Feedback submitted successfully!"
    return render_template("feedback_form.html", event_id=event_id)

# ----------------------
# Run App
# ----------------------
if __name__=="__main__":
    app.run(debug=True)
