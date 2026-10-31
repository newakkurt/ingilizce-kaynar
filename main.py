import os
import json
import random
import requests
import asyncio
from gtts import gTTS
from google import genai
from telegram import Bot

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

# ---------------- Persistent learning history ----------------
STATE_FILE = "learning_state.json"
MAX_HISTORY = 180

def load_learning_state():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as handle:
            state = json.load(handle)
        if not isinstance(state, dict):
            raise ValueError("Invalid learning state")
        state.setdefault("words", {})
        state.setdefault("recent", [])
        return state
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        return {"words": {}, "recent": []}

def choose_non_repeating_item(item, state):
    recent = {str(x).strip().casefold() for x in state.get("recent", [])}
    word = str(item.get("word", "")).strip()
    if word and word.casefold() not in recent:
        return item
    candidates = [x for x in BACKUP_VOCABULARY
                  if str(x.get("word", "")).strip().casefold() not in recent]
    return random.choice(candidates) if candidates else item

def save_learning_state(state, item):
    word = str(item.get("word", "")).strip()
    if not word:
        return
    key = word.casefold()
    record = state.setdefault("words", {}).setdefault(
        key, {"word": word, "times_sent": 0}
    )
    record["times_sent"] = int(record.get("times_sent", 0)) + 1
    from datetime import datetime, timezone
    record["last_sent_utc"] = datetime.now(timezone.utc).isoformat()
    recent = [x for x in state.setdefault("recent", [])
              if str(x).casefold() != key]
    recent.append(word)
    state["recent"] = recent[-MAX_HISTORY:]
    state["total_sent"] = int(state.get("total_sent", 0)) + 1
    with open(STATE_FILE, "w", encoding="utf-8") as handle:
        json.dump(state, handle, ensure_ascii=False, indent=2)

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
            model='gemini-2.5-flash',
            contents=prompt,
        )
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
    except Exception as e:
        print(f"Gemini API kota/erişim hatası alındı: {e}")
        print("🔄 Kota sınırına takıldığı için otomatik olarak yedek kelime havuzuna geçiliyor!")
        return random.choice(BACKUP_VOCABULARY)

def generate_image_for_word(word, example):
    """Ücretsiz ve API key istemeyen Pollinations AI servisi ile kelimeye özel görsel üretir"""
    prompt = f"A professional, minimalist, high-quality conceptual illustration representing the English word '{word}'. Context: {example}. Clean background, vibrant colors, modern vector art style."
    encoded_prompt = requests.utils.quote(prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=576&nologo=true"
    
    try:
        response = requests.get(image_url, timeout=15)
        if response.status_code == 200:
            image_path = "word_image.jpg"
            with open(image_path, "wb") as f:
                f.write(response.content)
            return image_path
    except Exception as e:
        print(f"Görsel üretilemedi: {e}")
    return None

async def main_async():
    token = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("Hata: Telegram Secret değerleri bulunamadı!")
        return

    bot = Bot(token=token)
    
    print("İçerik üretiliyor...")
    learning_state = load_learning_state()
    item = choose_non_repeating_item(generate_english_content(), learning_state)
    if not item:
        print("İçerik alınamadı.")
        return

    # 1. Metin Mesajı Hazırlığı
    message = (
        f"🤖 <b>AI Word of the Moment</b>\n\n"
        f"📌 <b>{item['word']}</b> <i>({item['type']})</i>\n"
        f"💡 <i>{item['definition']}</i>\n\n"
        f"🇬🇧 <b>EN:</b> {item['example']}\n"
        f"🇹🇷 <b>TR:</b> {item['tr_meaning']} — {item['tr_example']}"
    )

    # 2. Görsel gönder; görsel servisi hata verirse metin paylaşımını sürdür.
    image_path = generate_image_for_word(item['word'], item['example'])
    text_sent = False
    if image_path and os.path.exists(image_path):
        try:
            with open(image_path, 'rb') as photo:
                await bot.send_photo(chat_id=chat_id, photo=photo, caption=message, parse_mode="HTML")
            text_sent = True
        except Exception as e:
            print(f"Görselli mesaj gönderilemedi, metin deneniyor: {e}")
    if not text_sent:
        await bot.send_message(chat_id=chat_id, text=message, parse_mode="HTML")
    if image_path and os.path.exists(image_path):
        os.remove(image_path)
    save_learning_state(learning_state, item)

    # 3. Sesli Okuma Dosyası (Voice) Gönderme
    speech_text = f"{item['word']}. {item['example']}"
    audio_file = "voice.mp3"
    tts = gTTS(text=speech_text, lang='en', slow=False)
    tts.save(audio_file)

    with open(audio_file, 'rb') as voice:
        await bot.send_voice(chat_id=chat_id, voice=voice)

    if os.path.exists(audio_file):
        os.remove(audio_file)

    print("Otomatik paylaşım başarıyla gönderildi!")

if __name__ == "__main__":
    asyncio.run(main_async())
