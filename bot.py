import telebot
import requests
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

class KeepAliveHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")
    def log_message(self, format, *args):
        pass

def keep_alive():
    port = int(os.environ.get('PORT', 8000))
    server = HTTPServer(('0.0.0.0', port), KeepAliveHandler)
    Thread(target=server.serve_forever, daemon=True).start()

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN environment variable is not set")

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "✨ بەخێرهاتی بۆ بۆتی ڕووناکی قورئان ✨\n\n"
        "📖 بۆ خوێندنەوەی هەر ئایەتێک و وەرگێڕانی کوردی، ژمارەی سورەت و ئایەتەکە بەم شێوازە بنێرە:\n"
        "👈 `ژمارەی سورەت:ژمارەی ئایەت`\n\n"
        "📝 نموونە:\n"
        "`2:255` (بۆ خوێندنەوەی ئایەتەلوکورسی)\n"
        "`1:1` (بۆ خوێندنەوەی یەکەم ئایەتی فاتیحە)\n\n"
        "┄─»🔹«─┄\n"
        "🛠️ بۆ هەر کێشە، پێشنیار یاخود سەرنجێک نامە بنێرە بۆ گەشەپێدەر:\n"
        "👤 @Ahma\_dd0"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def get_quran_verse(message):
    text = message.text.strip()
    if ":" not in text:
        bot.reply_to(message, "⚠️ تکایە ژمارەی سورەت و ئایەتەکە بەم شێوازە بنوسە -> `1:1`")
        return
    try:
        surah, ayah = text.split(":", 1)
        msg = bot.send_message(message.chat.id, "⏳ خەریکم ئایەتەکە لە داتابەیسی فەرمی دەهێنم...", reply_to_message_id=message.message_id)
        arabic_url = f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}"
        kurdish_url = f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/ku.asan"
        res_ar = requests.get(arabic_url, timeout=5).json()
        res_ku = requests.get(kurdish_url, timeout=5).json()
        if res_ar['code'] == 200 and res_ku['code'] == 200:
            arabic_text = res_ar['data']['text']
            kurdish_text = res_ku['data']['text']
            surah_name = res_ar['data']['surah']['name']
            response = (
                f"📖 **{surah_name}** (ئایەتی {ayah})\n"
                f"┄─»🔹«─┄\n\n"
                f"🌿  `{arabic_text}`  🌿\n\n"
                f"┄─»🔸 وەرگێڕانی کوردی 🔸«─┄\n\n"
                f"💬 {kurdish_text}"
            )
            bot.edit_message_text(response, message.chat.id, msg.message_id, parse_mode="Markdown")
        else:
            bot.edit_message_text("❌ ببوورە، ئەو ئایەتە یان سورەتە بوونی نییە. (قورئان ١١٤ سورەتە).", message.chat.id, msg.message_id)
    except requests.exceptions.Timeout:
        bot.edit_message_text("⚠️ کاتەکەی بەسەرچوو! هێڵی داتابەیسەکە کەمێک خاوە، تکایە کەمێکی تر تاقی بکەرەوە.", message.chat.id, msg.message_id)
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, "⚠️ کێشەیەک ڕوویدا، دڵنیابەوە کە ژمارەکانت ڕاست نووسیوە.")

keep_alive()
bot.infinity_polling()
