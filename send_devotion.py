import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
import re
import xml.etree.ElementTree as ET

def get_taiwan_date():
    tw_tz = timezone(timedelta(hours=8))
    return datetime.now(tw_tz)

def get_youtube_from_playlist():
    """從播放清單 RSS 取得最新影片"""
    playlist_id = "PLfLZDCstmTXdFexWzM6X9z94zFdmUe8GC"
    rss_url = f"https://www.youtube.com/feeds/videos.xml?playlist_id={playlist_id}"
    
    try:
        response = requests.get(rss_url, timeout=30)
        root = ET.fromstring(response.content)
        
        # 找到最新的影片（第一個 entry）
        ns = {'atom': 'http://www.w3.org/2005/Atom', 'yt': 'http://www.youtube.com/xml/schemas/2015'}
        entry = root.find('atom:entry', ns)
        
        if entry is not None:
            video_id = entry.find('yt:videoId', ns)
            if video_id is not None:
                return f"https://youtu.be/{video_id.text}"
    except Exception as e:
        print(f"YouTube RSS 錯誤: {e}")
    
    return ""

def get_devotion_info(date):
    date_str = date.strftime("%Y%m%d")
    url = f"https://www.breadoflif
