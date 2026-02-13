import edge_tts
import tempfile
import weakref
from pathlib import Path
from moviepy import AudioFileClip, vfx
from moviepy.audio.fx import AudioFadeOut
from typing import Optional
from src.config import settings
from src.utils.logging_config import logging
from moviepy.audio.AudioClip import AudioClip, CompositeAudioClip
import numpy as np

class TTSService:
    def __init__(self, voice: str = None):
        self.voice = voice or settings.tts_voice
        self.est_sec_per_char = getattr(settings, "tts_est_sec_per_char", 0.18)
        self.default_padding = 0.3  # 300ms nghỉ

    async def generate_smart_audio(
        self,
        text: str,
        start_time: float,
        end_time: float,
        index: int,
        temp_dir: Path,
        padding: float = None
    ) -> AudioFileClip:
        """
        Tạo audio clip thông minh:
        - Tự động tính toán tốc độ để khớp với (duration - padding).
        - Tạo khoảng nghỉ tự nhiên.
        - Xử lý fade-out nếu buộc phải cắt.
        """
        total_duration = end_time - start_time
        padding_sec = padding if padding is not None else self.default_padding
        
        # Thời gian thực tế dành cho giọng đọc (phải trừ đi khoảng nghỉ)
        target_audio_duration = total_duration - padding_sec

        if target_audio_duration <= 0.5:
            # Nếu slot quá ngắn (<0.5s), không thể đọc kịp -> Force thời gian tối thiểu
            logging.warning(f"[{index}] Slot quá ngắn ({total_duration}s), giảm padding.")
            target_audio_duration = total_duration # Bỏ padding để ưu tiên nội dung

        # Tạo file tạm
        temp_file = tempfile.NamedTemporaryFile(
            dir=temp_dir,
            suffix=".mp3",
            delete=False
        )
        temp_path = Path(temp_file.name)
        temp_file.close()  # đóng để edge-tts có thể ghi

        # --- GIAI ĐOẠN 1: ƯỚC LƯỢNG BAN ĐẦU ---
        est_duration = len(text) * self.est_sec_per_char
        current_rate_str = "+0%"
        current_speed_factor = 1.0 # Hệ số tốc độ hiện tại (1.0 là bình thường)
        
        # Nếu ước lượng ban đầu đã lố -> Tính ngay rate cần thiết
        if est_duration > target_audio_duration:
            # Tính hệ số cần tăng: ví dụ cần nhanh gấp 1.2 lần
            needed_factor = est_duration / target_audio_duration
            increase_percent = int((needed_factor - 1) * 100)
            max_increase = settings.max_speed_increase_percent
            # Giới hạn trần (ví dụ max +50%)
            increase_percent = min(increase_percent, max_increase)
            current_rate_str = f"+{increase_percent}%"
            current_speed_factor = 1 + (increase_percent / 100)

        clip = None
        # final_file_path = temp_path # Lưu path cuối cùng để dùng

        try:
            # --- GIAI ĐOẠN 2: TINH CHỈNH (RETRY LOOP) ---
            # Thử tối đa 3 lần để đạt độ khớp hoàn hảo
            for attempt in range(3):
                # 1. Gọi Edge TTS
                comm = edge_tts.Communicate(text, self.voice, rate=current_rate_str)
                await comm.save(str(temp_path))

                # 2. Đóng clip cũ để giải phóng tài nguyên trước khi load lại
                if clip: 
                    clip.close()
                    del clip

                # --- FIX LỖI ACCESSING TIME TẠI ĐÂY ---
                raw_clip = AudioFileClip(str(temp_path))
                # Không cắt safety nữa
                clip = raw_clip
                actual_dur = clip.duration

                logging.info(
                    f"[{index}] Try {attempt+1}: Rate={current_rate_str}, "
                    f"Raw={clip.duration:.2f}s -> Safe={actual_dur:.2f}s / Target={target_audio_duration:.2f}s"
                )

                # 4. Kiểm tra điều kiện thoát (Cho phép lố 0.1s vẫn chấp nhận được)
                if actual_dur <= target_audio_duration + 0.1:
                    break
                
                # 5. Nếu vẫn lố thời gian -> Tính toán lại Rate
                # Logic mới: Tính dựa trên Tốc độ tích lũy (Cumulative Speed)
                # Tốc độ mới = Tốc độ cũ * (Độ dài hiện tại / Độ dài mục tiêu)
                
                overshoot_ratio = actual_dur / target_audio_duration
                new_speed_factor = current_speed_factor * overshoot_ratio * 1.05
                new_percent = int((new_speed_factor - 1) * 100)
                max_increase = settings.max_speed_increase_percent

                if new_percent >= max_increase:
                    current_rate_str = f"+{max_increase}%"
                    break 
                
                current_rate_str = f"+{new_percent}%"
                current_speed_factor = 1 + (new_percent / 100)
            
            # --- GIAI ĐOẠN 3: XỬ LÝ HẬU KỲ ---
            # Nếu clip dài hơn target, cắt bớt (không fade)
            if clip.duration > target_audio_duration:
                clip = clip.subclipped(0, target_audio_duration)

            # Tạo composite với duration chính xác (thay vì dùng with_duration)
            actual_duration = clip.duration
            if actual_duration < total_duration:
                # Bọc trong CompositeAudioClip để tự động thêm silence
                clip = CompositeAudioClip([clip])
                clip = clip.with_duration(total_duration)  # Composite tự xử lý out-of-bounds
            else:
                # Nếu audio dài hơn hoặc bằng total_duration, đã cắt ở trên, giữ nguyên
                pass

            clip = clip.with_start(start_time)

            # Đăng ký dọn dẹp
            self._register_cleanup(clip, temp_path)

            return clip
            
        except Exception as e:
            # Xóa file tạm ngay nếu có lỗi
            if temp_path.exists():
                temp_path.unlink()
            logging.error(f"[{index}] lỗi khi tạo audio: {e}")
            raise
    

    def _register_cleanup(self, clip: AudioFileClip, temp_path: Path) -> None:
        """
        Đăng ký hàm xóa file tạm khi clip được garbage collected.
        """
        def cleanup():
            try:
                if temp_path.exists():
                    temp_path.unlink()
                    # logging.debug(f"Deleted temp: {temp_path}")
            except Exception:
                pass
        weakref.finalize(clip, cleanup)