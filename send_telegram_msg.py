import os
from dotenv import load_dotenv
load_dotenv()


def send_telegram_notification(chat_id, message, parse_mode='HTML'):
    """
    Envia notificação push via Telegram bot.
    
    Args:
        message: O texto da mensagem a ser enviada
        parse_mode: Formato do texto - 'HTML' ou 'Markdown'
    
    A função falha silenciosamente se as credenciais não estiverem configuradas
    ou se houver erro ao enviar, para não quebrar o pipeline principal.
    """
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not bot_token or not chat_id:
        return
    
    try:
        import requests
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        payload = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': parse_mode,
            'disable_web_page_preview': True
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            print(f"Telegram notification sent successfully")
        else:
            print(f"Warning: Telegram notification failed with status {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"Warning: Failed to send Telegram notification: {e}")



notification_message = f"""
<b>📰 Novo Briefing Disponível</b>

<b>Feed:</b> gaming
<b>Artigos:</b> 20
<b>ID:</b> 39

Acesse em: https://rain.galdinho.news
"""


send_telegram_notification(901434795, notification_message)