from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import hashlib

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(50)) #doctor, nurse, pharma
    otp_secret = db.Column(db.String(16)) #2fa

    def set_password(self, password):
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()

    def check_password(self, password):
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()
    
class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
    content = db.Column(db.LargeBinary)
    is_sensitive = db.Column(db.Boolean)

class Prescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
    drug_name = db.Column(db.String(100))
    dosage = db.Column(db.String(100))