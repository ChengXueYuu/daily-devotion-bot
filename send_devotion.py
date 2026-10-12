import requests
from datetime import datetime, timezone, timedelta
import re
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_taiwan_date():
    tw_tz = timezone(timedelta(hours=8))
    return datetime.now(tw_tz)

def get_youtube_for_date(date_str, api_key):
    channel_id = "UClDpY60wBFG-j2VEI4kQplQ"
    search_url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "key": api_key,
        "channelId": channel_id,
        "q": "每日靈糧 " + date_str,
        "type": "video",
        "order": "date",
        "maxResults": 5,
        "part": "snippet",
    }
    try:
        response = requests.get(search_url, params=params, timeout=30)
        data = response.json()
        for item in data.get("items", []):
            title = item["snippet"]["title"]
            video_id = item["id"]["videoId"]
            if date_str in title:
                yt_url = "https://youtu.be/" + video_id
                scripture_match = re.search(r'【每日靈糧】(.+?)｜', title)
                scripture = scripture_match.group(1).strip() if scripture_match else ""
                pastor_match = re.search(r'｜(.+?)_\d{8}', title)
                pastor = pastor_match.group(1).strip() if pastor_match else ""
                return {'url': yt_url, 'title': title, 'scripture': scripture, 'pastor': pastor}
    except Exception as e:
        print("YouTube API error: " + str(e))
    return {'url': '', 'title': '', 'scripture': '', 'pastor': ''}

def get_devotion_info(date, api_key):
    date_str = date.strftime("%Y%m%d")
    base_url = "https://www.breadoflife.taipei/type_devotional/"
    url = base_url + date_str + "/"

    youtube_info = get_youtube_for_date(date_str, api_key)
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
    api_key = os.environ.get('GOOGLE_API_KEY')
    today = get_taiwan_date()
    info = get_devotion_info(today, api_key)
    
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
