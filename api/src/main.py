import requests
import json
import os
from src.douyin_config import DouyinConfig
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    try:
        msToken = create_msToken()
        ttwid = create_ttwid()
        return {"status": 200, "msToken": msToken, "ttwid": ttwid}
    except Exception as e:
        return {"status": 500, "error": str(e)}

def call_douyin_feed_api(api_url, headers, params=None):
    try:
        response = requests.get(api_url, headers=headers, params=params, timeout=10)
        response.raise_for_status() 
        
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi gọi API: {e}")
        return None

def parse_video_urls(feed_data):
    video_list = []
    
    if not feed_data or 'aweme_list' not in feed_data:
        print("Không tìm thấy dữ liệu 'aweme_list' hợp lệ.")
        return []

    for item in feed_data['aweme_list']:
        try:
            desc = item.get('desc', 'no_title')
            
            video_info = item.get('video', {})
            
            play_addr = video_info.get('play_addr', {})
            
            url_list = play_addr.get('url_list', [])
            
            if url_list:
                video_url = url_list[0]
                
                video_list.append({
                    'id': item.get('aweme_id'),
                    'title': desc,
                    'url': video_url
                })
        except Exception as e:
            print(f"Lỗi khi parse item: {e}")
            continue
            
    return video_list

def download_video(url, filename, headers):
    try:
        with requests.get(url, headers=headers, stream=True) as r:
            r.raise_for_status()
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"Đã tải xong: {filename}")
        return True
    except Exception as e:
        print(f"Lỗi khi tải video {filename}: {e}")
        return False

def create_msToken():
    try:
        response = requests.get("http://douyin-downloader/api/douyin/web/generate_real_msToken")
        response.raise_for_status()
        msToken = response.json().get("data").get("msToken")
        return msToken
    except requests.exceptions.RequestException as e:
        return f"Đã có lỗi xảy ra: {e}"
    
def create_xbogus():
    try:
        response = requests.get("http://douyin-downloader/api/douyin/web/generate_real_msToken")
        response.raise_for_status()
        msToken = response.json().get("data").get("msToken")
        return msToken
    except requests.exceptions.RequestException as e:
        return f"Đã có lỗi xảy ra: {e}"
    
def create_abogus():
    try:
        response = requests.get("http://douyin-downloader/api/douyin/web/generate_real_msToken")
        response.raise_for_status()
        msToken = response.json().get("data").get("msToken")
        return msToken
    except requests.exceptions.RequestException as e:
        return f"Đã có lỗi xảy ra: {e}"

def create_ttwid():
    try:
        response = requests.get("http://douyin-downloader/api/douyin/web/generate_ttwid")
        response.raise_for_status()
        msToken = response.json().get("data").get("ttwid")
        return msToken
    except requests.exceptions.RequestException as e:
        return f"Đã có lỗi xảy ra: {e}"


# if __name__ == "__main__":
#     my_config = DouyinConfig(
#         cookie="ttwid=1%7C...; odin_tt=...; sessionid=...",
#         x_bogus="DFSzswVLZ...",
#         signature="_02B4Z..."
#     )
#     API_URL = "https://www.douyin.com/aweme/v1/web/tab/feed/" 
    
#     MY_HEADERS = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...", 
#         "Cookie": "douyin.com; passport_csrf_token=...; ttwid=...",
#         "Referer": "https://www.douyin.com/"
#     }
    
#     MY_PARAMS = {
#         "device_platform": "webapp",
#         "aid": "6383",
#         "channel_id": "0",
#         "count": "10",
#         # Các tham số mã hóa khác bạn đã có:
#         # "X-Bogus": "...",
#         # "_signature": "..."
#     }

#     print("Đang lấy dữ liệu feed...")
#     data = call_douyin_feed_api(API_URL, MY_HEADERS, MY_PARAMS)
    
#     if data:
#         videos = parse_video_urls(data)
#         print(f"Tìm thấy {len(videos)} video.")
        
#         if not os.path.exists('downloads'):
#             os.makedirs('downloads')
            
#         if len(videos) > 0:
#             first_video = videos[0]
#             print(f"Đang tải: {first_video['title']}")
            
#             safe_title = "".join([c for c in first_video['title'] if c.isalnum() or c in (' ', '-', '_')]).strip()
#             file_path = f"downloads/{safe_title[:50]}.mp4"
            
#             download_video(first_video['url'], file_path, MY_HEADERS)