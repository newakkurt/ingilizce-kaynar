import os
import json
import random
import requests
from gtts import gTTS
from google import genai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

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

async def send_word_content(chat_id, context):
    """Kelimeyi, ses dosyasını ve görseli oluşturup Telegram'a gönderir"""
    item = generate_english_content()
    if not item:
        await context.bot.send_message(chat_id=chat_id, text="İçerik alınamadı.")
        return

    # 1. Metin Mesajı
    message = (
        f"🤖 <b>AI Word of the Moment</b>\n\n"
        f"📌 <b>{item['word']}</b> <i>({item['type']})</i>\n"
        f"💡 <i>{item['definition']}</i>\n\n"
        f"🇬🇧 <b>EN:</b> {item['example']}\n"
        f"🇹🇷 <b>TR:</b> {item['tr_meaning']} — {item['tr_example']}"
    )

    # 2. Görsel Üretme ve Gönderme
    image_path = generate_image_for_word(item['word'], item['example'])
    if image_path and os.path.exists(image_path):
        with open(image_path, 'rb') as photo:
            await context.bot.send_photo(chat_id=chat_id, photo=photo, caption=message, parse_mode="HTML")
        os.remove(image_path)
    else:
        await context.bot.send_message(chat_id=chat_id, text=message, parse_mode="HTML")

    # 3. Sesli Okuma Dosyası (Voice)
    speech_text = f"{item['word']}. {item['example']}"
    audio_file = "voice.mp3"
    tts = gTTS(text=speech_text, lang='en', slow=False)
    tts.save(audio_file)

    with open(audio_file, 'rb') as voice:
        await context.bot.send_voice(chat_id=chat_id, voice=voice)

    if os.path.exists(audio_file):
        os.remove(audio_file)

# Komut Fonksiyonları
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot aktif! İngilizce kelime paylaşımı için /paylas komutunu kullanabilirsin.")

async def yardim_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📖 <b>Bot Komutları Rehberi:</b>\n\n"
        "• /paylas - Yapay zeka ile anlık yeni bir İngilizce kelime, özel görsel ve sesli telaffuz gönderir.\n"
        "• /yardim - Bu yardım menüsünü görüntüler."
    )
    await update.message.reply_text(help_text, parse_mode="HTML")

async def paylas_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text("🔍 Yeni kelime ve görsel hazırlanıyor, lütfen bekleyin...")
    await send_word_content(chat_id, context)

def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN")
    if not token:
        print("Hata: TELEGRAM_BOT_TOKEN bulunamadı!")
        return

    application = ApplicationBuilder().token(token).build()

    # Komut yönlendiricileri
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("yardim", yardim_command))
    application.add_handler(CommandHandler("paylas", paylas_command))

    print("Bot çalışmaya başladı (Polling modunda dinleniyor)...")
    application.run_polling()

if __name__ == "__main__":
    main()
