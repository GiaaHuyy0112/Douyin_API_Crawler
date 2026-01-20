from dataclasses import dataclass
from typing import Dict

@dataclass
class DouyinConfig:
    cookie: str
    x_bogus: str
    signature: str
    msToken: str
    
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    referer: str = "https://www.douyin.com/"
    
    device_platform: str = "webapp"
    aid: str = "6383"
    channel_id: str = "0"
    version_code: str = "170400"
    
    def get_headers(self) -> Dict[str, str]:
        return {
            "User-Agent": self.user_agent,
            "Referer": self.referer,
            "Cookie": self.cookie
        }

    def get_params(self, cursor: int = 0, count: int = 10) -> Dict[str, str]:
        """
        Trả về dictionary params đầy đủ để đưa vào requests.
        LƯU Ý: Nếu cursor thay đổi, X-Bogus thường cũng phải tính lại.
        Ở đây tôi giả định bạn đang dùng X-Bogus tương ứng với cursor này.
        """
        return {
            "device_platform": self.device_platform,
            "aid": self.aid,
            "channel_id": self.channel_id,
            "pc_client_type": "1",
            "version_code": self.version_code,
            "version_name": "17.4.0",
            "cookie_enabled": "true",
            "screen_width": "1920",
            "screen_height": "1080",
            "browser_language": "en-US",
            "browser_platform": "Win32",
            "browser_name": "Chrome",
            "browser_version": "120.0.0.0",
            "browser_online": "true",
            "engine_name": "Blink",
            "engine_version": "120.0.0.0",
            "os_name": "Windows",
            "os_version": "10",
            "cpu_core_num": "8",
            "device_memory": "8",
            "platform": "PC",
            "downlink": "10",
            "effective_type": "4g",
            "round_trip_time": "50",
            "cursor": str(cursor),
            "count": str(count),
            "X-Bogus": self.x_bogus,
            "_signature": self.signature,
            "msToken": self.msToken
        }