import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
import re

def get_taiwan_date():
    tw_tz = timezone(timedelta(hours=8))
    return datetime.now(tw_tz)

def get_devotion_info(date):
    date_str = date.strftime("%Y%m%d")
    url = f"https://www.breadoflife.taipei/type_devotional/{date_str}/"
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        scripture = ""
        title_tag = soup.find('title')
        if title_tag and '|' in title_tag.get_text():
            scripture = title_tag.get_text().split('|')[0].strip()
        
        youtube_url = ""
        match = re.search(r'youtube\.com/embed/([a-zA-Z0-9_-]+)', response.text)
        if match:
            youtube_url = f"https://youtu.be/{match.group(1)}"
        
        return {'date': date.strftime("%Y-%m-%d"), 'scripture': scripture or "請點擊連結查看", 'web_url': url, 'youtube_url': youtube_url}
    except:
        return {'date': date.strftime("%Y-%m-%d"), 'scripture': "請點擊連結查看", 'web_url': url, 'youtube_url': ""}

def send_line_message(message, token, target_id):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    data = {"to": target_id, "messages": [{"type": "text", "text": message}]}
    requests.post(url, headers=headers, json=data)

def main():
    import os
    token = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
    target_id = os.environ.get('LINE_TARGET_ID')
    
    today = datetime(2026, 1, 27, tzinfo=timezone(timedelta(hours=8)))
    info = get_devotion_info(today)
    
    message = f"📖 {info['date']} | {info['scripture']}\n🔗 {info['web_url']}"
    if info['youtube_url']:
        message += f"\n🎬 {info['youtube_url']}"
    
    send_line_message(message, token, target_id)
    print("✅ 發送成功！")

if __name__ == "__main__":
    main()
