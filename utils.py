from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
from flask_login import current_user
from functools import wraps
from flask import abort
import pyotp
import qrcode
import io


AES_KEY = b'ThisIsASecretKey'

def encrypt_data(data):
    cipher = AES.new(AES_KEY, AES.MODE_CFB)
    return cipher.iv + cipher.encrypt(data.encode())

def decrypt_data(ciphertext):
    iv = ciphertext[:16]
    cipher = AES.new(AES_KEY, AES.MODE_CFB, iv=iv)
    return cipher.decrypt(ciphertext[16:]).decode()

def role_required(*roles):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated
    return wrapper

def generate_otp_secret():
    return pyotp.random_base32()

def verify_otp(secret, token):
    totp = pyotp.TOTP(secret)
    return totp.verify(token)

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role != 'admin':
            return "Access denied", 403
        return f(*args, **kwargs)
    return decorated

def generate_qr_code(username, otp_secret):
    otp_uri = pyotp.totp.TOTP(otp_secret).provisioning_uri(name=username, issuer_name="HealthVault")
    qr = qrcode.make(otp_uri)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    qr_b64 = base64.b64encode(buffer.getvalue()).decode()
    return otp_uri, f"data:image/png;base64,{qr_b64}"

