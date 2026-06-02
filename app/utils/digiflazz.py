import hashlib
import requests
import os
from dotenv import load_dotenv

# Wajib dipanggil agar kunci di .env pasti terbaca
load_dotenv()

BASE_URL = "https://api.digiflazz.com/v1"

def generate_signature(command):
    """Membuat signature MD5 sesuai aturan Digiflazz"""
    username = os.getenv('DIGIFLAZZ_USERNAME')
    api_key = os.getenv('DIGIFLAZZ_API_KEY')
    
    # Format: username + api_key + command
    sign_str = f"{username}{api_key}{command}"
    return hashlib.md5(sign_str.encode()).hexdigest()

def cek_saldo():
    """Mengirim request ke Digiflazz untuk cek saldo"""
    username = os.getenv('DIGIFLAZZ_USERNAME')
    
    payload = {
        "cmd": "deposit",
        "username": username,
        # PERBAIKAN: Gunakan kata "depo" sesuai dokumentasi Digiflazz
        "sign": generate_signature("depo") 
    }
    
    try:
        response = requests.post(f"{BASE_URL}/cek-saldo", json=payload)
        return response.json()
    except Exception as e:
        return {"data": None, "error": str(e)}
    
def cek_harga(brand=""):
    username = os.getenv('DIGIFLAZZ_USERNAME')
    api_key = os.getenv('DIGIFLAZZ_API_KEY')
    
    # PENTING: Signature untuk tarik harga adalah "pricelist", BUKAN "depo"
    sign_str = f"{username}{api_key}pricelist"
    signature = hashlib.md5(sign_str.encode()).hexdigest()
    
    payload = {
        "cmd": "prepaid",
        "username": username,
        "sign": signature
    }
    
    try:
        response = requests.post("https://api.digiflazz.com/v1/price-list", json=payload)
        result = response.json()
        
        # Kirimkan data utuh apa adanya (biar ditangani dengan aman oleh routes.py)
        # Jika error, result.get("data") akan berisi dictionary pesan error
        # Jika sukses, result.get("data") akan berisi list produk
        return {"status": "success", "data": result.get("data", [])}
        
    except Exception as e:
        return {"status": "error", "message": f"Sistem Error: {str(e)}"}
    
def proses_topup(target_id, sku, order_id):
    """Mengirim perintah ke Digiflazz untuk mengisi diamond ke pembeli"""
    username = os.getenv('DIGIFLAZZ_USERNAME')
    
    # Untuk transaksi, Digiflazz meminta signature dari ref_id (Order ID)
    payload = {
        "username": username,
        "buyer_sku_code": sku,
        "customer_no": target_id,
        "ref_id": order_id,
        "sign": generate_signature(order_id) 
    }
    
    try:
        response = requests.post(f"{BASE_URL}/transaction", json=payload)
        return response.json()
    except Exception as e:
        return {"data": {"status": "Gagal", "message": str(e)}}