from wsgiref import headers
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
        a_bogus = create_abogus()
        x_bogus = create_xbogus()
        return {"status": 200, "msToken": msToken, "ttwid": ttwid, "a_bogus": a_bogus, "x_bogus": x_bogus}
    except Exception as e:
        return {"status": 500, "error": str(e)}
    
@app.get("/feed")
def root():
    try:
        msToken = create_msToken()
        ttwid = create_ttwid()
        a_bogus = create_abogus()
        x_bogus = create_xbogus()
        svwebid = create_svwebid()

        data = fetch_douyin_hot_search(bogus=a_bogus, mstoken=msToken, ttwid=ttwid, svwebid=svwebid)
        
        return {"status": 200, "data": data}
    except Exception as e:
        return {"status": 500, "error": str(e)}
    
    
def fetch_douyin_hot_search(bogus=None, cookie=None, mstoken=None, ttwid=None, svwebid=None):
    uifid = "5bdad390e71fd6e6e69e3cafe6018169c2447c8bc0b8484cc0f203a274f99fdb9cf7a4d1e0b69a920c6ca4ad980608788e76671ef24a5084040fdb53a9732ecf1200212c1e7826103933f21370c4cd85147e664fa82539303108b24e10c61c78d8c0d2ca2d0b88dfec4b28fbcb3330df93732eb113d2a1693459da96c31496d7ac617ff67394a29e3341caf3ab79fbf7838a1adc248fdaacbace735542dd91bf"
    
    # --- 2. FULL PARAMETERS ---
    params = {
        "device_platform": "webapp",
        "aid": "6383",
        "channel": "channel_pc_web",
        "detail_list": "1",
        "source": "6",
        "main_billboard_count": "5",
        "update_version_code": "170400",
        "pc_client_type": "1",
        "pc_libra_divert": "Windows",
        "support_h265": "1",
        "support_dash": "1",
        "cpu_core_num": "8",
        "version_code": "170400",
        "version_name": "17.4.0",
        "cookie_enabled": "true",
        "screen_width": "1920",
        "screen_height": "1080",
        "browser_language": "vi-VN",
        "browser_platform": "Win32",
        "browser_name": "Chrome",
        "browser_version": "143.0.0.0",
        "browser_online": "true",
        "engine_name": "Blink",
        "engine_version": "143.0.0.0",
        "os_name": "Windows",
        "os_version": "10",
        "device_memory": "8",
        "platform": "PC",
        "downlink": "4.45",
        "effective_type": "4g",
        "round_trip_time": "50",
        "webid": "7600804439108453926",
        "uifid": uifid,
        "verifyFp": svwebid,
        "fp": svwebid,
        "msToken": mstoken,
        "a_bogus": bogus
    }

    # --- 3. FULL HEADERS ---
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
        "priority": "u=1, i",
        "referer": "https://www.douyin.com/?recommend=1",
        "sec-ch-ua": '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "uifid": uifid,
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
    }

    # --- 4. FULL COOKIES (Parsed from your -b string) ---
    # If you have a full cookie string, you can use: 
    # cookies = {c.split('=')[0]: c.split('=')[1] for c in custom_cookie_str.split('; ')}
    cookies = {
        "__ac_nonce": "0697b7b67009c910188d3",
        "__ac_signature": "_02B4Z6wo00f01h4SFSQAAIDCfAwRYED.9JYeMhGAAO8O6e",
        "enter_pc_once": "1",
        "UIFID_TEMP": "5bdad390e71fd6e6e69e3cafe6018169c2447c8bc0b8484cc0f203a274f99fdb9cf7a4d1e0b69a920c6ca4ad98060878d3b7900073919d9753d60cb2e849edf99a42cb95bb5e203d4561dcbdaa5ba50b",
        "x-web-secsdk-uid": "c7f5b884-c7a5-4823-a30c-4996ea2b3640",
        "s_v_web_id": svwebid,
        "device_web_cpu_core": "8",
        "device_web_memory_size": "8",
        "architecture": "amd64",
        "hevc_supported": "true",
        "dy_swidth": "1920",
        "dy_sheight": "1080",
        "is_dash_user": "1",
        "passport_csrf_token": "372f0c75fc6a3373936632242bb9b6de",
        "odin_tt": "d5919a42bbe339d3c0204298655300868ba3ea167df34ba1ebb3403693c5129d941796d0f04b5a811e91949e1a075c7309b4535c4a1f166c95737704c345db9246c7441a1058a612ce0e302be54668eb",
        "UIFID": uifid,
        "ttwid": ttwid,
        "IsDouyinActive": "true"
    }

    try:
        response = requests.get(
            "https://www.douyin.com/aweme/v1/web/hot/search/list/",
            params=params,
            headers=headers,
            cookies=cookies,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

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

def create_svwebid():
    try:
        response = requests.get("http://douyin-downloader/api/douyin/web/generate_s_v_web_id")
        response.raise_for_status()
        svwebid = response.json().get("data").get("svwebid")
        return svwebid
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