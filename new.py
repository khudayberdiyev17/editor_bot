from telethon import TelegramClient, events, Button
from deep_translator import GoogleTranslator
import re
from config import *

bot = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

def grammar_cleanup(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'(\.{2,})', '.', text)
    text = re.sub(r'\b(\w+)( \1\b)+', r'\1', text, flags=re.IGNORECASE)
    return text.strip().capitalize()

def translate_text(original: str) -> str:
    langs = {'uz': '🇺🇿 O‘zbek', 'en': '🇬🇧 English', 'ru': '🇷🇺 Rus',}
    translations = []
    for lang, flag in langs.items():
        try:
            t = GoogleTranslator(source='auto', target=lang).translate(original)
            t = grammar_cleanup(t)
            translations.append(f"{flag}:\n{t}")
        except Exception as e:
            translations.append(f"{flag}:\n[Xatolik: {e}]")
    return "\n\n".join(translations)

def split_message(text: str, limit=4000):
    """Uzun matnlarni telegram limiti bo‘yicha bo‘lib yuborish"""
    return [text[i:i+limit] for i in range(0, len(text), limit)]

@bot.on(events.NewMessage(chats=CHANNEL_ID))
async def handler(event):
    try:
        message = event.message

        # Bot o‘zi yuborgan bo‘lsa – ignore
        if message.out:
            return

        original_text = message.message or ""
        translations = translate_text(original_text)
        final_text = f"{translations}\n\n👉 {KANAL_LINK}"

        buttons = [[Button.url("📢 Do‘stlarga ulashish", KANAL_LINK)]]

        # Eski postni o‘chirib tashlash
        await bot.delete_messages(CHANNEL_ID, message.id)

        # Media bo‘lsa, faqat caption sifatida kanal linkini yuborish (tarjimalar caption uchun uzun bo‘lishi mumkin emas)
        if message.media and message.media.__class__.__name__ != "MessageMediaWebPage":
            await bot.send_file(CHANNEL_ID, file=message.media, caption=f"👉 {KANAL_LINK}", buttons=buttons)
            # Tarjimalarni alohida yuborish
            for part in split_message(translations):
                await bot.send_message(CHANNEL_ID, part, buttons=buttons)
        else:
            for part in split_message(final_text):
                await bot.send_message(CHANNEL_ID, part, buttons=buttons)

        print(f"[OK] Post #{message.id} qayta joylandi")

    except Exception as e:
        print(f"[X] Xatolik: {e}")

print("Bot ishga tushdi...")
bot.run_until_disconnected()