from functools import wraps
from flask import request, jsonify, session, redirect, url_for
import time
import hmac
import hashlib
import os

# --- 1. SISTEM RATE LIMITER (Anti-Spam Checkout) ---
ip_records = {}

def limit_requests(max_requests=5, window=60):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            ip = request.remote_addr
            current_time = time.time()
            
            if ip in ip_records:
                ip_records[ip] = [t for t in ip_records[ip] if current_time - t < window]
            else:
                ip_records[ip] = []
                
            if len(ip_records[ip]) >= max_requests:
                return jsonify({
                    "status": "error", 
                    "message": "Terlalu banyak permintaan! Sistem mendeteksi spam. Tunggu 1 menit."
                }), 429 
                
            ip_records[ip].append(current_time)
            return f(*args, **kwargs)
        return wrapped
    return decorator


# --- 2. SISTEM IP WHITELISTING (Pelindung Webhook Duitku) ---
def verify_duitku_ip(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        ALLOWED_IPS = [
            '13.228.25.108', 
            '52.220.100.86', 
            '127.0.0.1',     
        ]
        
        client_ip = request.remote_addr
        
        if client_ip not in ALLOWED_IPS:
            return jsonify({
                "status": "error",
                "message": "Akses Ditolak! Alamat IP Anda diblokir oleh sistem keamanan PixeTopup."
            }), 403 
            
        return f(*args, **kwargs)
    return wrapped


# --- 3. SISTEM OTENTIKASI ADMIN ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function


# --- 4. SISTEM PELINDUNG WEBHOOK DIGIFLAZZ ---
def verify_digiflazz_webhook(f):
    """Memverifikasi signature HMAC SHA1 dari Digiflazz"""
    @wraps(f)
    def wrapped(*args, **kwargs):
        signature_header = request.headers.get('X-Hub-Signature')
        if not signature_header:
            return jsonify({"status": "error", "message": "Signature tidak ditemukan"}), 403
            
        webhook_secret = os.getenv('DIGIFLAZZ_WEBHOOK_SECRET', 'secret_default')
        payload = request.get_data()
        
        # Hitung signature menggunakan HMAC SHA1
        expected_signature = 'sha1=' + hmac.new(
            webhook_secret.encode('utf-8'),
            payload,
            hashlib.sha1
        ).hexdigest()
        
        if not hmac.compare_digest(signature_header, expected_signature):
            return jsonify({"status": "error", "message": "Signature tidak valid! Akses Ditolak."}), 403
            
        return f(*args, **kwargs)
    return wrapped