import requests
from src.douyin_config import DouyinConfig
from ruamel.yaml import YAML

def serialize_cookies(cookie_dict):
    return ";".join([f"{key}={value}" for key, value in cookie_dict.items()])
    
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
    
def update_cookies(new_cookies):
    try:
        data = {"service": "douyin_web", "cookies": new_cookies}
        reponse = requests.post("http://douyin-downloader/api/hybrid/update_cookie", data=data)
        reponse.raise_for_status()
        return reponse.json()
    except requests.exceptions.RequestException as e:
        return f"Đã có lỗi xảy ra: {e}"
    
    
def update_douyin_cookie(file_path, new_cookie_string):
    yaml = YAML()
    # Mở file để đọc và ghi (r+) giúp giữ nguyên file hiện tại trên Docker mount
    with open(file_path, 'r+', encoding='utf-8') as f:
        config = yaml.load(f)
        config['TokenManager']['douyin']['headers']['Cookie'] = new_cookie_string
        
        f.seek(0) # Quay lại đầu file
        yaml.dump(config, f)
        f.truncate() # Xóa nội dung thừa phía sau nếu file mới ngắn hơn file cũ
    print("Đã cập nhật cookie thành công trong Docker mount.")
    return {"status": "success", "message": "Cookie đã được cập nhật trong file cấu hình."}

def fetch_user_posts(id, max_count=10):
    try:
        response = requests.get(f"http://douyin-downloader/api/douyin/web/fetch_user_post_videos?sec_user_id={id}&max_cursor=0&count={max_count}")
        response.raise_for_status()
        data = response.json()
        urls = get_video_urls(data)
        return {"status": "success", "urls": urls}
    except requests.exceptions.RequestException as e:
        return f"Đã có lỗi xảy ra: {e}"
    
def get_video_urls(obj):
    video_urls = []
    
    aweme_list = obj.get("data", {}).get("aweme_list", [])
    
    for item in aweme_list:
        # Lấy danh sách url từ play_addr
        urls = item.get("video", {}).get("play_addr", {}).get("url_list", [])
        if urls:
            video_urls.append(urls[0])
            
    return video_urls