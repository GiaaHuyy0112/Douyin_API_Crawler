import edge_tts
import tempfile
from pathlib import Path
import asyncio
from moviepy import AudioFileClip
from typing import Optional
from src.config import settings

class TTSService:
    def __init__(self, voice: str = None):
        self.voice = voice or settings.tts_voice

    async def generate_smart_audio(
        self,
        text: str,
        start_time: float,
        end_time: float,
        index: int,
        temp_dir: Path
    ) -> AudioFileClip:
        """
        Tạo audio clip với điều chỉnh tốc độ nếu cần.
        Trả về AudioFileClip đã được set start time.
        """
        limit = end_time - start_time
        # Tạo file tạm, tự động xoá khi clip bị del hoặc dùng context
        temp_file = tempfile.NamedTemporaryFile(
            dir=temp_dir,
            suffix=".mp3",
            delete=False
        )
        temp_path = Path(temp_file.name)
        temp_file.close()  # đóng để edge-tts có thể ghi

        try:
            # Tạo lần đầu với tốc độ mặc định
            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save(str(temp_path))
            
            clip = AudioFileClip(str(temp_path))
            actual_duration = clip.duration
            
            # Nếu quá dài, tăng tốc
            if actual_duration > limit + 0.1:  # dung sai 0.1s
                speed_factor = actual_duration / limit
                increase = min(
                    int((speed_factor - 1) * 100),
                    settings.max_speed_increase_percent
                )
                rate = f"+{increase}%"
                
                # Tạo lại với tốc độ mới
                communicate = edge_tts.Communicate(text, self.voice, rate=rate)
                await communicate.save(str(temp_path))
                
                # Đóng clip cũ và tạo mới
                clip.close()
                clip = AudioFileClip(str(temp_path))
            
            # Gán thời gian bắt đầu
            clip = clip.with_start(start_time)
            
            # Lưu đường dẫn file tạm vào attribute để có thể xoá sau
            clip._temp_audio_path = temp_path
            return clip
            
        except Exception as e:
            # Xoá file tạm nếu có lỗi
            if temp_path.exists():
                temp_path.unlink()
            raise e