from src.douyin_config import DouyinConfig
from src.utils import *
from fastapi import FastAPI

app = FastAPI()

@app.get("/update_cookies")
def root():
    try:
        msToken = create_msToken()
        ttwid = create_ttwid()
        a_bogus = create_abogus()
        x_bogus = create_xbogus()
        svwebid = create_svwebid()
        
        cookies = {
            "enter_pc_once": "1",
            "UIFID_TEMP": "5bdad390e71fd6e6e69e3cafe6018169c2447c8bc0b8484cc0f203a274f99fdb9cf7a4d1e0b69a920c6ca4ad98060878d3b7900073919d9753d60cb2e849edf99a42cb95bb5e203d4561dcbdaa5ba50b",
            "s_v_web_id": svwebid,
            "hevc_supported": "true",
            "dy_swidth": "1920",
            "dy_sheight": "1080",
            "is_dash_user": "1",
            "passport_csrf_token": "372f0c75fc6a3373936632242bb9b6de",
            "passport_csrf_token_default": "372f0c75fc6a3373936632242bb9b6de",
            "odin_tt": "d5919a42bbe339d3c0204298655300868ba3ea167df34ba1ebb3403693c5129d941796d0f04b5a811e91949e1a075c7309b4535c4a1f166c95737704c345db9246c7441a1058a612ce0e302be54668eb",
            "__security_mc_1_s_sdk_crypt_sdk": "15acf9ea-4304-89a6",
            "bd_ticket_guard_client_web_domain": "2",
            "fpk1": "U2FsdGVkX183HNZHTeoguv8v/hb45/euFbZUOwqWAAQVSivjIEFiwDMAed2pebXj2cpMKoPvFM4frCE4ou+KOg==",
            "fpk2": "89db729cfcdc129111f017b0e7ac324a",
            "UIFID": "5bdad390e71fd6e6e69e3cafe6018169c2447c8bc0b8484cc0f203a274f99fdb9cf7a4d1e0b69a920c6ca4ad980608788e76671ef24a5084040fdb53a9732ecf1200212c1e7826103933f21370c4cd85147e664fa82539303108b24e10c61c78d8c0d2ca2d0b88dfec4b28fbcb3330df93732eb113d2a1693459da96c31496d7ac617ff67394a29e3341caf3ab79fbf7838a1adc248fdaacbace735542dd91bf",
            "volume_info": "%7B%22isUserMute%22%3Afalse%2C%22isMute%22%3Atrue%2C%22volume%22%3A0.5%7D",
            "download_guide": "%223%2F20260129%2F0%22",
            "__ac_nonce": "0697e2a8700b691bab6a0",
            "__ac_signature": "_02B4Z6wo00f01KaQYeQAAIDAxI5looovR1ymsGVAAEDe42",
            "device_web_cpu_core": "8",
            "device_web_memory_size": "8",
            "architecture": "amd64",
            "stream_recommend_feed_params": "%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A1920%2C%5C%22screen_height%5C%22%3A1080%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A8%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A10%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A50%7D%22",
            "strategyABtestKey": "%221769876109.289%22",
            "home_can_add_dy_2_desktop": "%221%22",
            "bd_ticket_guard_client_data": "eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCS2thclJ4Q0ErUzVuN0pXaVBVTXpUdS9JVUFnNHRHM0t4Q3RNMEdnc0dZMWpBQVc5dGF5UGpkWkg5U284VDJNU1ZIZy9jY0d3SVE4Ui83VWFBVVF4U3c9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoyfQ%3D%3D",
            "bd_ticket_guard_client_data_v2": "eyJyZWVfcHVibGljX2tleSI6IkJLa2FyUnhDQStTNW43SldpUFVNelR1L0lVQWc0dEczS3hDdE0wR2dzR1kxakFBVzl0YXlQamRaSDlTbzhUMk1TVkhnL2NjR3dJUThSLzdVYUFVUXhTdz0iLCJyZXFfY29udGVudCI6InNlY190cyIsInJlcV9zaWduIjoicUhwaktNdDEzZ25Qa1NsNWhOclVrM2N0K2hHSFBXTG5nOVlMdXIvbmw5VT0iLCJzZWNfdHMiOiIjc3pRUUwzRTd2cmY0eTliZE9RQVZ6WFMzbzdWdkg5ZThaWXlDaUNwVzFRMFhLMTFCSjdRTThNRGxvUGlxIn0%3D",
            "gulu_source_res": "eyJwX2luIjoiNjU5NTEzOWNiNWY3ZDAzY2U1YmNkZjNlM2M2MDQwZjk0N2JiNGVkYWUzZjc5N2FhNzAzZjczZDcwZjlmODQyMSJ9",
            "sdk_source_info": "7e276470716a68645a606960273f276364697660272927676c715a6d6069756077273f276364697660272927666d776a68605a607d71606b766c6a6b5a7666776c7571273f275e58272927666a6b766a69605a696c6061273f27636469766027292762696a6764695a7364776c6467696076273f275e582729277672715a646971273f2763646976602729277f6b5a666475273f2763646976602729276d6a6e5a6b6a716c273f2763646976602729276c6b6f5a7f6367273f27636469766027292771273f2731343031343433323d3c333234272927676c715a75776a716a666a69273f2763646976602778",
            "bit_env": "lbpmv__HuVXu610l-br78emQ2b7uKM_7B-VLTVVlwk_t95SNPvhCqmlseQqWMBM6ehEu7msSriqZNnDVS_49bfbs5KaXN9iOqxu-9WEyUeH_5t6JhM5SQl4kSWek92INzuhgmPVxv43xR1Es9mRg470PKGfSxlc1Wf9cA9Gag6ZOY8C1bu2_6mhZW7QV2aiakai0tcLBX3orUfaqauUiHABEgMSUMwmLEUF5NVzyKTRTiOBSjlXOHcM9mo4IcoPKv3C9tubnWDenY_sX1GourT9EWx581Ddso5Rfa1aDmUxVChwwpByujTJVZL6ZA0ttaWacP51E1BTcmSN6jV7AeZDfoTvXNj4cEv-xe9bpQzVv5kQuMWH2P49rnBzUy6BkLJN2WbggqOXXYQdpfdEeUbVWyTlD0mYETThMPUwdBDP__-ji-sB2i0c0f1U3vCXKjnn3soJEN2PpDb388GP_b5G3Rxtt8iSRH6hcnJzSwjM2BSe3FFPUw2wAxH1v8PuK",
            "passport_auth_mix_state": "ko35htvxt1kaixclmkwcyj2duhlljeh6vih0o6wty0czlq2p",
            "record_force_login": "%7B%22timestamp%22%3A1769876121652%2C%22force_login_video%22%3A7%2C%22force_login_live%22%3A0%2C%22force_login_direct_video%22%3A0%7D",
            "ttwid": ttwid,
            "biz_trace_id": "219cf3c0",
            "IsDouyinActive": "false",
            "stream_player_status_params": "%22%7B%5C%22is_auto_play%5C%22%3A0%2C%5C%22is_full_screen%5C%22%3A0%2C%5C%22is_full_webscreen%5C%22%3A1%2C%5C%22is_mute%5C%22%3A1%2C%5C%22is_speed%5C%22%3A1%2C%5C%22is_visible%5C%22%3A0%7D%22"
        }
        
        serialized_cookies = serialize_cookies(cookies)
        status = update_douyin_cookie("/app/crawlers/douyin/web/config.yaml",serialized_cookies)
        
        return status
        
    except Exception as e:
        return {"status": 500, "error": str(e)}
    
@app.get("/feed_user_videos")
def root():
    try:
        # userID = "MS4wLjABAAAAarOBhxJoW72Gahflo_RnuDtLH0moQU1aC-_Wt9D0XHhs_Eoss5GpyS6fjwAEm8RR"
        userID = "MS4wLjABAAAATd30q_hSWE0klt7V-5NspJvXmS5LY9Y6HySunSi1FXdwosqAqAVjSdkRVv5_pvGP"
        data = fetch_user_posts(userID, max_count=30)
        return {"status": 200, "data": data}
    except Exception as e:
        return {"status": 500, "error": str(e)}
    