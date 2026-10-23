import os
import random
import requests

# Günde 4 kez dönmesi için sade kelime havuzu
VOCABULARY_LIST = [
    {
        "word": "Resilient",
        "definition": "able to withstand or recover quickly from difficult conditions",
        "example": "He is resilient enough to handle tough situations at work.",
        "tr_meaning": "dayanıklı, esnek",
        "tr_example": "İşteki zor durumların üstesinden gelebilecek kadar dayanıklıdır."
    },
    {
        "word": "Enhance",
        "definition": "intensify, increase, or further improve the quality or value of",
        "example": "Automating tasks will greatly enhance overall productivity.",
        "tr_meaning": "artırmak, geliştirmek",
        "tr_example": "Görevleri otomatikleştirmek genel verimliliği büyük ölçüde artıracaktır."
    },
    {
        "word": "Consistent",
        "definition": "acting or done in the same way over time to be fair or accurate",
        "example": "Consistent effort is the key to mastering a new skill.",
        "tr_meaning": "tutarlı, kararlı",
        "tr_example": "Kararlı çaba, yeni bir beceride uzmanlaşmanın anahtarıdır."
    },
    {
        "word": "Implement",
        "definition": "put a decision, plan, or agreement into effect",
        "example": "We plan to implement new automation tools next week.",
        "tr_meaning": "uygulamaya koymak, kurmak",
        "tr_example": "Gelecek hafta yeni otomasyon araçlarını uygulamaya koymayı planlıyoruz."
    }
]

def send_telegram_message():
    token = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("Hata: Secret değerleri bulunamadı!")
        return

    item = random.choice(VOCABULARY_LIST)

    # İstenen 3 satırlık sade format
    message = (
        f"1. <b>{item['word']}</b>: {item['definition']}\n"
        f"2. {item['example']}\n"
        f"3. <b>TR:</b> {item['tr_meaning']} — {item['tr_example']}"
    )

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
        print(f"Hata oluştu. Kod: {response.status_code}, Yanıt: {response.text}")

if __name__ == "__main__":
    send_telegram_message()
