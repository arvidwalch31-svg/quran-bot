bot.py
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
    server = HTTPServer(('0.0.0.0', 8000), KeepAliveHandler)
    Thread(target=server.serve_forever, daemon=True).start()

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN environment variable is not set")

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "✨ بەخێرهاتی بۆ بۆتی ڕووناکی قورئان ✨\n\n"
        "📖 بۆ خوێندنە
