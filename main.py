import os
import random
import requests
from gtts import gTTS

VOCABULARY_LIST = [
    {
        "word": "Resilient",
        "type": "adj",
        "definition": "Quick to recover from difficulties.",
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

def send_telegram_bot():
    token = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("Hata: Secret değerleri bulunamadı!")
        return

    item = random.choice(VOCABULARY_LIST)

    # 1. Yazılı Mesaj
    message = (
        f"📌 <b>{item['word']}</b> <i>({item['type']})</i>\n"
        f"💡 <i>{item['definition']}</i>\n\n"
        f"🇬🇧 <b>EN:</b> {item['example']}\n"
        f"🇹🇷 <b>TR:</b> {item['tr_meaning']} — {item['tr_example']}"
    )

    url_text = f"https://api.telegram.org/bot{token}/sendMessage"
    payload_text = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    requests.post(url_text, json=payload_text)

    # 2. Sesli Okuma (Kelime ve Örnek Cümle İngilizce Okunur)
    speech_text = f"{item['word']}. {item['example']}"
    audio_file = "voice.mp3"
    
    tts = gTTS(text=speech_text, lang='en', slow=False)
    tts.save(audio_file)

    # 3. Ses Dosyasını Telegram'a Gönderme (sendVoice)
    url_voice = f"https://api.telegram.org/bot{token}/sendVoice"
    with open(audio_file, 'rb') as voice:
        files = {'voice': voice}
        data = {'chat_id': chat_id}
        response = requests.post(url_voice, data=data, files=files)

    if response.status_code == 200:
        print("Yazı ve Ses mesajı başarıyla gönderildi!")
    else:
        print(f"Ses gönderilirken hata oluştu: {response.text}")

    # Geçici ses dosyasını sil
    if os.path.exists(audio_file):
        os.remove(audio_file)

if __name__ == "__main__":
    send_telegram_bot()
