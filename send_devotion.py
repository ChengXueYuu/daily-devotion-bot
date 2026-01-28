import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
import xml.etree.ElementTree as ET

def get_taiwan_date():
    tw_tz = timezone(timedelta(hours=8))
    return datetime.now(tw_tz)

def get_youtube_for_date(date_str):
    playlist_id = "PLfLZDCstmTXdFexWzM6X9z94zFdmUe8GC"
    rss_url = "https://www.youtube.com/feeds/videos.xml?playlist_id=" + playlist_id
    try:
        response = requests.get(rss_url, timeout=30)
        root = ET.fromstring(response.content)
        ns = {'atom': 'http://www.w3.org/2005/Atom', 'yt': 'http://www.youtube.com/xml/schemas/2015'}
        for entry in root.findall('atom:entry', ns):
            title = entry.find('atom:title', ns)
            if title is not None and date_str in title.text:
                video_id = entry.find('yt:videoId', ns)
                if video_id is not None:
                    return "https://youtu.be/" + video_id.text
    except Exception as e:
        print("YouTube RSS error: " + str(e))
    return ""

def get_devotion_info(date):
    date_str = date.strftime("%Y%m%d")
    base_url = "https://www.breadoflife.taipei/type_devotional/"
    url = base_url + date_str + "/"
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        scripture = ""
        title_tag = soup.find('title')
        if title_tag and '|' in title_tag.get_text():
            scripture = title_tag.get_text().split('|')[0].strip()
        youtube_url = get_youtube_for_date(date_str)
        return {'date': date.strftime("%Y-%m-%d"), 'scripture': scripture or "請點擊連結查看", 'web_url': url, 'youtube_url': youtube_url}
    except Exception as e:
        print("Error: " + str(e))
        return {'date': date.strftime("%Y-%m-%d"), 'scripture': "請點擊連結查看", 'web_url': url, 'youtube_url': ""}

def send_line_message(message, token, target_id):
    api_url = "https://api.line.me/v2/bot/message/push"
    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + token}
    data = {"to": target_id, "messages": [{"type": "text", "text": message}]}
    response = requests.post(api_url, headers=headers, json=data)
    print("LINE API status: " + str(response.status_code))

def main():
    import os
    token = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
    target_id = os.environ.get('LINE_TARGET_ID')
    today = get_taiwan_date()
    info = get_devotion_info(today)
    print("Date: " + info['date'])
    print("Scripture: " + info['scripture'])
    print("URL: " + info['web_url'])
    print("YouTube: " + info['youtube_url'])
    message = "📖 " + info['date'] + " | " + info['scripture'] + "\n🔗 " + info['web_url']
    if info['youtube_url']:
        message = message + "\n🎬 " + info['youtube_url']
    send_line_message(message, token, target_id)
    print("Done!")

if __name__ == "__main__":
    main()
