import os
import json
import random
import requests
from gtts import gTTS
from google import genai

# Kota dolu olduğunda veya API'ye ulaşılamadığında devreye girecek yedek havuz
BACKUP_VOCABULARY = [
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

def generate_english_content():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("API anahtarı bulunamadı, yedek havuz kullanılıyor.")
        return random.choice(BACKUP_VOCABULARY)

    client = genai.Client(api_key=api_key)
    prompt = """
    You are an expert English teacher. Provide a useful, B1-B2 level English vocabulary word or phrasal verb.
    Return strictly raw JSON format without markdown code blocks, backticks, or extra text.

    Required JSON Structure:
    {
        "word": "Word",
        "type": "adj/v/noun/phrasal verb",
        "definition": "Short English definition (max 8 words)",
        "example": "Short English example sentence (max 8 words)",
        "tr_meaning": "Türkçe kısa anlamı",
        "tr_example": "Türkçe kısa cümle çevirisi"
    }
    """

    try:
        print("Gemini API isteği atılıyor...")
        response = client.models.generate_content(
            model='gemini-3.8-flash',
            contents=prompt,
        )
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
    except Exception as e:
        print(f"Gemini API kota/erişim hatası alındı: {e}")
        print("🔄 Kota sınırına takıldığı için otomatik olarak yedek kelime havuzuna geçiliyor!")
        return random.choice(BACKUP_VOCABULARY)

def send_telegram_bot():
    token = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("Hata: Telegram Secret değerleri bulunamadı!")
        return

    item = generate_english_content()
    if not item:
        print("İçerik alınamadı.")
        return

    # 1. Yazılı Mesaj
    message = (
        f"🤖 <b>AI Word of the Moment</b>\n\n"
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

    # 2. Sesli Okuma (Kelime ve Örnek Cümle)
    speech_text = f"{item['word']}. {item['example']}"
    audio_file = "voice.mp3"
    
    tts = gTTS(text=speech_text, lang='en', slow=False)
    tts.save(audio_file)

    # 3. Ses Dosyasını Telegram'a Gönderme
    url_voice = f"https://api.telegram.org/bot{token}/sendVoice"
    with open(audio_file, 'rb') as voice:
        files = {'voice': voice}
        data = {'chat_id': chat_id}
        requests.post(url_voice, data=data, files=files)

    if os.path.exists(audio_file):
        os.remove(audio_file)

    print("Yazı ve ses mesajı başarıyla gönderildi!")

if __name__ == "__main__":
    send_telegram_bot()
