import os
import requests

def send_telegram_message(message):
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("Hata: Secret değerleri (TELEGRAM_TOKEN veya TELEGRAM_CHAT_ID) bulunamadı!")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("Mesaj başarıyla gönderildi!")
    else:
        print(f"Mesaj gönderilemedi. Hata kodu: {response.status_code}, Yanıt: {response.text}")

if __name__ == "__main__":
    send_telegram_message("🚀 <b>Test Mesajı:</b> GitHub Actions ve Telegram Bot entegrasyonu başarıyla çalışıyor!")