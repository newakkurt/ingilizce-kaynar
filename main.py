import os
import json
import time
import requests
from gtts import gTTS
from google import genai

def generate_english_content(retries=3, delay=5):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Hata: GEMINI_API_KEY bulunamadı!")
        return None

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

    for attempt in range(1, retries + 1):
        try:
            print(f"Gemini API isteği atılıyor (Deneme {attempt}/{retries})...")
            response = client.models.generate_content(
                model='gemini-3.8-flash',
                contents=prompt,
            )
            # Markdown kod bloklarını temizle
            clean_text = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)
        except Exception as e:
            print(f"Gemini API hatası (Deneme {attempt}): {e}")
            if attempt < retries:
                print(f"{delay} saniye bekleniyor ve tekrar deneniyor...")
                time.sleep(delay)
            else:
                print("Maksimum deneme sayısına ulaşıldı.")
                return None

def send_telegram_bot():
    token = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("Hata: Telegram Secret değerleri bulunamadı!")
        return

    item = generate_english_content()
    if not item:
        print("İçerik üretilemediği için mesaj gönderilmedi.")
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

    print("Yapay zeka içeriği ve ses mesajı başarıyla gönderildi!")

if __name__ == "__main__":
    send_telegram_bot()
