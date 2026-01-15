from fastapi import FastAPI, Query
import requests
from urllib.parse import quote

app = FastAPI()

douyin_url = (
    "https://www.douyin.com/aweme/v1/web/aweme/detail/"
    "?aweme_id=7148736076176215311"
    "&device_platform=webapp"
    "&aid=6383"
    "&channel=channel_pc_web"
    "&pc_client_type=1"
    "&version_code=170400"
    "&version_name=17.4.0"
    "&cookie_enabled=true"
    "&screen_width=1920"
    "&screen_height=1080"
    "&browser_language=zh-CN"
    "&browser_platform=Win32"
    "&browser_name=Edge"
    "&browser_version=117.0.2045.47"
    "&browser_online=true"
    "&engine_name=Blink"
    "&engine_version="
)

user_agent = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/90.0.4430.212 Safari/537.36"
)

DOUYIN_URL = "https://www.douyin.com/aweme/v1/web/tab/feed/"

# Hàm gửi request Douyin
def fetch_douyin_feed(count: int, x_bogus: str, cookie: str):
    params = {
        "count": count,
        "X-Bogus": x_bogus
    }
    headers = {
        "Cookie": cookie,
        "Referer": "https://www.douyin.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    }
    resp = requests.get(DOUYIN_URL, params=params, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()

@app.get("/douyin/feed")
def get_feed(
    # count: int = Query(10, ge=1, le=50),
    # x_bogus: str = Query(..., description="X-Bogus signature"),
    # cookie: str = Query(..., description="Cookie gồm sid_guard, msToken, …")
):
    # data = fetch_douyin_feed(count, x_bogus, cookie)
    data = generate_x_bogus(douyin_url,user_agent)
    return {"feed": data}



def generate_x_bogus(
    douyin_url: str,
    user_agent: str,
    base_api: str = "http://douyin-downloader:80/api/douyin/web/generate_x_bogus",
    timeout: int = 10
) -> dict:
    """
    Gọi service generate X-Bogus nội bộ (tương đương curl đã cung cấp)

    :param douyin_url: URL gốc của Douyin (chưa encode)
    :param user_agent: User-Agent gốc (chưa encode)
    :param base_api: Endpoint generate_x_bogus
    :param timeout: timeout request (seconds)
    :return: JSON response (dict)
    """

    params = {
        "url": quote(douyin_url, safe=""),
        "user_agent": quote(user_agent, safe="")
    }

    headers = {
        "accept": "application/json"
    }

    response = requests.get(
        base_api,
        params=params,
        headers=headers,
        timeout=timeout
    )

    response.raise_for_status()
    return response.json()
