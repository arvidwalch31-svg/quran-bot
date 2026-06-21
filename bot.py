import telebot
import requests
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN environment variable is not set")

bot = telebot.TeleBot(BOT_TOKEN)

ALL_SURAHS = [
    "1. الفاتحة", "2. البقرة", "3. آل عمران", "4. النساء", "5. المائدة", "6. الأنعام",
    "7. الأعراف", "8. الأنفال", "9. التوبة", "10. يونس", "11. هود", "12. يوسف",
    "13. الرعد", "14. إبراهيم", "15. الحجر", "16. النحل", "17. الإسراء", "18. الكهف",
    "19. مريم", "20. طه", "21. الأنبياء", "22. الحج", "23. المؤمنون", "24. النور",
    "25. الفرقان", "26. الشعراء", "27. النمل", "28. القصص", "29. العنکبوت", "30. الروم",
    "31. لقمان", "32. السجدة", "33. الأحزاب", "34. سبأ", "35. فاطر", "36. يس",
    "37. الصافات", "38. ص", "39. الزمر", "40. غافر", "41. فصلت", "42. الشورى",
    "43. الزخرف", "44. الدخان", "45. الجاثية", "46. الأحقاف", "47. محمد", "48. الفتح",
    "49. الحجرات", "50. ق", "51. الذاريات", "52. الطور", "53. النجم", "54. القمر",
    "55. الرحمن", "56. الواقعة", "57. الحديد", "58. المجادلة", "59. الحشر", "60. الممتحنة",
    "61. الصف", "62. الجمعة", "63. المنافقون", "64. التغابن", "65. الطلاق", "66. التحريم",
    "67. الملك", "68. القلم", "69. الحاقة", "70. المعارج", "71. نوح", "72. الجن",
    "73. المزمل", "74. المدثر", "75. القيامة", "76. الإنسان", "77. المرسلات", "78. النبأ",
    "79. النازعات", "80. عبس", "81. التکوير", "82. الإنفطار", "83. المطففين", "84. الانشقاق",
    "85. البروج", "86. الطارق", "87. الأعلى", "88. الغاشية", "89. الفجر", "90. البلد",
    "91. الشمس", "92. الليل", "93. الضحى", "94. الشرح", "95. التين", "96. العلق",
    "97. القدر", "98. البينة", "99. الزلزلة", "100. العاديات", "101. القارعة", "102. التکاثر",
    "103. العصر", "104. الهمزة", "105. الفيل", "106. قريش", "107. الماعون", "108. الكوثر",
    "109. الكافرون", "110. النصر", "111. المسد", "112. الإخلاص", "113. الفلق", "114. الناس"
]

ITEMS_PER_PAGE = 10

def generate_page_text(page):
    start_idx = page * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    page_items = ALL_SURAHS[start_idx:end_idx]
    text = f"📜 **لیستی سورەتەکانی قورئان (پەیجی {page + 1} لە ١٢):**\n\n"
    for item in page_items:
        text += f"🔹 {item}\n"
    text += "\n💡 ژمارەی تەنیشت ناوەکە بەکاربێنە بۆ گەڕان (نموونە -> `2:255`)"
    return text

def generate_markup(page):
    markup = InlineKeyboardMarkup()
    buttons = []
    if page > 0:
        buttons.append(InlineKeyboardButton("⬅️ پێشوو", callback_data=f"page_{page-1}"))
    if (page + 1) * ITEMS_PER_PAGE < len(ALL_SURAHS):
        buttons.append(InlineKeyboardButton("داهاتوو ➡️", callback_data=f"page_{page+1}"))
    markup.row(*buttons)
    return markup

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

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    try:
        bot.set_my_commands([
            BotCommand("start", "دەستپێکردنەوەی بۆت"),
            BotCommand("list", "لیستی ١١٤ سورەتەکە")
        ])
    except Exception as e:
        print(e)
    welcome_text = (
        "✨ بەخێرهاتی بۆ بۆتی ڕووناکی قورئان ✨\n\n"
        "📖 بۆ خوێندنەوەی هەر ئایەتێک و وەرگێڕانی کوردی، ژمارەی سورەت و ئایەتەکە بەم شێوازە بنێرە:\n"
        "👈 `ژمارەی سورەت:ژمارەی ئایەت`\n\n"
        "📜 بۆ بینینی لیستی سورەتەکان، کلیک لە سەر /list بکە.\n\n"
        "📝 نموونە:\n"
        "`2:255` (بۆ خوێندنەوەی ئایەتەلوکورسی)\n"
        "┄─»🔹«─┄\n"
        "🛠️ گەشەپێدەر:\n"
        "👤 @Ahma\_dd0"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(commands=['list'])
def send_surah_list(message):
    text = generate_page_text(0)
    markup = generate_markup(0)
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('page_'))
def handle_page_click(call):
    page = int(call.data.split('_')[1])
    text = generate_page_text(page)
    markup = generate_markup(page)
    try:
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
    except Exception as e:
        pass

@bot.message_handler(func=lambda message: True)
def get_quran_verse(message):
    text = message.text.strip()
    if ":" not in text:
        bot.reply_to(message, "⚠️ تکایە ژمارەی سورەت و ئایەتەکە بەم شێوازە بنوسە -> `1:1`\n📜 بۆ بینینی لیستی سورەتەکان بنووسە: /list")
        return
    try:
        surah, ayah = text.split(":", 1)
        msg = bot.send_message(message.chat.id, "⏳ خەریکم ئایەتەکە دەهێنم...", reply_to_message_id=message.message_id)
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
            bot.edit_message_text("❌ ببوورە، ئەو ئایەتە یان سورەتە بوونی نییە.", message.chat.id, msg.message_id)
    except requests.exceptions.Timeout:
        bot.edit_message_text("⚠️ کاتەکەی بەسەرچوو! تکایە کەمێکی تر تاقی بکەرەوە.", message.chat.id, msg.message_id)
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, "⚠️ کێشەیەک ڕوویدا، دڵنیابەوە کە ژمارەکانت ڕاست نووسیوە.")

keep_alive()
bot.infinity_polling()
