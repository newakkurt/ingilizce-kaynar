import os
import random
import requests

# Günde 4 kez gönderilecek örnek İngilizce kelime/içerik havuzu
VOCABULARY_LIST = [
    {
        "word": "Resilient",
        "type": "adjective",
        "meanings": ["dayanıklı", "esnek", "çabuk toparlanan"],
        "example": "He is resilient enough to handle tough situations at work."
    },
    {
        "word": "Enhance",
        "type": "verb",
        "meanings": ["geliştirmek", "artırmak", "zenginleştirmek"],
        "example": "Automating tasks will greatly enhance overall productivity."
    },
    {
        "word": "Consistent",
        "type": "adjective",
        "meanings": ["tutarlı", "kararlı", "sürekli"],
        "example": "Consistent effort is the key to mastering a new skill."
    },
    {
        "word": "Implement",
        "type": "verb",
        "meanings": ["uygulamaya koymak", "yürütmek", "kurmak"],
        "example": "We plan to implement new automation tools next week."
    }
]

def send_telegram_message():
    # .github/workflows/run.yml içerisindeki Secret isimleriyle tam uyumlu
    token = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("Hata: Secret değerleri bulunamadı!")
        return

    # Rastgele bir kelime seçelim
    item = random.choice(VOCABULARY_LIST)
    meanings_str = ", ".join(item["meanings"])

    # İngilizce formatlanmış mesaj şablonu
    message = (
        f"🇬🇧 <b>Word of the Day</b>\n\n"
        f"🔹 <b>{item['word']}</b> <i>({item['type']})</i>\n"
        f"💡 <b>Meaning:</b> {meanings_str}\n\n"
        f"📝 <b>Example Sentence:</b>\n"
        f"<i>\"{item['example']}\"</i>\n\n"
        f"⚙️ <i>Automated Daily English Notification</i>"
    )

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("İngilizce mesaj başarıyla gönderildi!")
    else:
        print(f"Hata oluştu. Kod: {response.status_code}, Yanıt: {response.text}")

if __name__ == "__main__":
    send_telegram_message()
