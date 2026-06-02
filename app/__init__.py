from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

# Membaca variabel dari file .env
load_dotenv()

# Inisialisasi objek database dan migrasi
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # Konfigurasi keamanan dan database
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'rahasia_pixietopup')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ==========================================
    # FILTER UNTUK FORMAT RUPIAH
    # ==========================================
    @app.template_filter('format_number')
    def format_number_filter(value):
        try:
            return "{:,}".format(int(value)).replace(',', '.')
        except (ValueError, TypeError):
            return value
    # ==========================================

    # Menyambungkan database dan migrasi ke aplikasi
    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        # Memanggil file models.py agar Flask mengenali tabel kita
        from . import models
        
        # db.create_all() SUDAH DINONAKTIFKAN! 
        # Kita sekarang menggunakan Flask-Migrate untuk mengatur tabel.

        from .routes import main
        app.register_blueprint(main)

    return app