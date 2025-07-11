from flask import Flask, render_template, redirect, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User, Note, Patient
from utils import encrypt_data, decrypt_data, verify_otp, role_required, admin_required, generate_otp_secret, generate_qr_code
from config import Config
from routes import register_blueprints

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
login_manager = LoginManager(app)

@app.route('/')
def home():
    return render_template("home.html")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            if verify_otp(user.otp_secret, request.form['otp']):
                login_user(user)
                return redirect('/dashboard')
            return "Invalid OTP"
        return "Invalid credentials"
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        #check if user already exists
        if User.query.filter_by(username=username).first():
            flash("Username already exists")
            return redirect('/register')

        #generate OTP secret
        otp_secret= generate_otp_secret()

        #create user
        user = User(username=username, role=role, otp_secret=otp_secret)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        otp_uri, qr_b64 = generate_qr_code(username, otp_secret)
        return render_template("register.html", otp_uri=otp_uri, otp_qr=qr_b64, otp_secret=otp_secret)
    return render_template("register.html", otp_uri=None, otp_qr=None, otp_secret=None)

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return render_template("home.html")

register_blueprints(app)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=7000) 