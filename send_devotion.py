import requests
from datetime import datetime, timezone, timedelta
import re
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_taiwan_date():
    tw_tz = timezone(timedelta(hours=8))
    return datetime.now(tw_tz)

def get_youtube_for_date(date_str):
    playlist_id = "PLfLZDCstmTXdFexWzM6X9z94zFdmUe8GC"
    rss_url = "https://www.youtube.com/feeds/videos.xml?playlist_id=" + playlist_id
    try:
        response = requests.get(rss_url, timeout=30)
        content = response.text
        
        entries = re.findall(r'<entry>(.*?)</entry>', content, re.DOTALL)
        
        for entry in entries:
            title_match = re.search(r'<title>(.*?)</title>', entry)
            video_id_match = re.search(r'<yt:videoId>(.*?)</yt:videoId>', entry)
            
            if title_match and video_id_match:
                title = title_match.group(1)
                video_id = video_id_match.group(1)
                
                if date_str in title:
                    yt_url = "https://youtu.be/" + video_id
                    
                    scripture_match = re.search(r'【每日靈糧】(.+?)｜', title)
                    scripture = ""
                    if scripture_match:
                        scripture = scripture_match.group(1).strip()
                    
                    pastor_match = re.search(r'｜(.+?)_\d{8}', title)
                    pastor = ""
                    if pastor_match:
                        pastor = pastor_match.group(1).strip()
                    
                    return {'url': yt_url, 'title': title, 'scripture': scripture, 'pastor': pastor}
    except Exception as e:
        print("YouTube RSS error: " + str(e))
    return {'url': '', 'title': '', 'scripture': '', 'pastor': ''}

def get_devotion_info(date):
    date_str = date.strftime("%Y%m%d")
    base_url = "https://www.breadoflife.taipei/type_devotional/"
    url = base_url + date_str + "/"
    
    youtube_info = get_youtube_for_date(date_str)
    return {
        'date': date.strftime("%Y-%m-%d"),
        'scripture': youtube_info['scripture'],
        'pastor': youtube_info['pastor'],
        'web_url': url,
        'youtube_url': youtube_info['url']
    }

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
    print("Pastor: " + info['pastor'])
    print("URL: " + info['web_url'])
    print("YouTube: " + info['youtube_url'])
    
    message = "🌅 早安，願神的話語成為今天的力量！\n\n"
    message = message + "📖 " + info['date'] + " | " + info['scripture'] + "\n"
    message = message + "🎤 " + info['pastor'] + "\n\n"
    message = message + "🔗 靈修網站：\n" + info['web_url']
    if info['youtube_url']:
        message = message + "\n\n🎬 影音靈修：\n" + info['youtube_url']
    
    send_line_message(message, token, target_id)
    print("Done!")

if __name__ == "__main__":
    main()
