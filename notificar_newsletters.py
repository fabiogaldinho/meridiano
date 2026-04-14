import os
import importlib
from dotenv import load_dotenv

load_dotenv()

from run_briefing import send_telegram_notification, TELEGRAM_CHAT_ID

newsletters = [
    {"id": 5, "feed": "brasil"},
    {"id": 6, "feed": "cyber-security"},
    {"id": 7, "feed": "gaming"},
    {"id": 8, "feed": "tech"},
]

for nl in newsletters:
    feed = nl["feed"]
    newsletter_id = nl["id"]
    
    try:
        feed_module = importlib.import_module(f"feeds.{feed}")
        chat_ids = getattr(feed_module, 'TELEGRAM_CHAT_ID', {TELEGRAM_CHAT_ID: f"https://galdinho.news/newsletters/{newsletter_id}"})
    except ImportError:
        chat_ids = {TELEGRAM_CHAT_ID: f"https://galdinho.news/newsletters/{newsletter_id}"}
    
    for chatid, chaturl in chat_ids.items():
        notification_message = f"""
<b>📰 Nova Newsletter Disponível</b>

<b>Feed:</b> {feed}
Acesse em: https://galdinho.news/newsletters/{newsletter_id}
        """
        send_telegram_notification(chatid, notification_message)
        print(f"✓ Notificação enviada: {feed} (ID {newsletter_id}) -> chat {chatid}")

print("\nTodas as notificações enviadas!")