import os
import random
import requests

# Kısa, öz ve pratik kelime/cümle havuzu
VOCABULARY_LIST = [
    {
        "word": "Resilient",
        "type": "adj",
        "definition": "Quick to recover from diffuculties.",
        "example": "Stay resilient in tough times.",
        "tr_meaning": "Dayanıklı, esnek",
        "tr_example": "Zor zamanlarda güçlü kal."
    },
    {
        "word": "Enhance",
        "type": "v",
        "definition": "To improve quality or value.",
        "example": "Coffee enhances my focus.",
        "tr_meaning": "Artırmak, geliştirmek",
        "tr_example": "Kahve odaklanmamı artırır."
    },
    {
        "word": "Consistent",
        "type": "adj",
        "definition": "Always acting in the same way.",
        "example": "Be consistent with your study.",
        "tr_meaning": "Kararlı, tutarlı",
        "tr_example": "Derslerinde kararlı ol."
    },
    {
        "word": "Implement",
        "type": "v",
        "definition": "To put a plan into action.",
        "example": "Let's implement this strategy.",
        "tr_meaning": "Uygulamaya koymak",
        "tr_example": "Bu stratejiyi uygulayalım."
    },
    {
        "word": "Crucial",
        "type": "adj",
        "definition": "Extremely important or decisive.",
        "example": "Timing is crucial for success.",
        "tr_meaning": "Çok önemli, kritik",
        "tr_example": "Başarı için zamanlama kritiktir."
    }
]

def send_telegram_message():
    token = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("Hata: Secret değerleri bulunamadı!")
        return

    item = random.choice(VOCABULARY_LIST)

    # Şık, simgeli ama kısa & net format
    message = (
        f"📌 <b>{item['word']}</b> <i>({item['type']})</i>\n"
        f"💡 <i>{item['definition']}</i>\n\n"
        f"🇬🇧 <b>EN:</b> {item['example']}\n"
        f"🇹🇷 <b>TR:</b> {item['tr_meaning']} — {item['tr_example']}"
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
