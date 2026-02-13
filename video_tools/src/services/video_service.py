import moviepy as mp
from pathlib import Path
from typing import List
import asyncio
from concurrent.futures import ThreadPoolExecutor
from src.services.tts_service import TTSService
from src.utils.srt_utils import parse_srt
from src.config import settings
from moviepy.audio.AudioClip import CompositeAudioClip

class VideoDubbingService:
    def __init__(self, tts_service: TTSService):
        self.tts_service = tts_service
        self.executor = ThreadPoolExecutor(max_workers=2)

    async def create_dubbed_video(
        self,
        video_path: Path,
        srt_path: Path,
        output_path: Path,
        temp_dir: Path = None
    ):
        """Tạo video lồng tiếng từ file SRT và video gốc."""
        if temp_dir is None:
            temp_dir = settings.temp_dir
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Đọc và phân tích SRT
        with open(srt_path, "r", encoding="utf-8") as f:
            content = f.read()
        segments = parse_srt(content)
        
        # Sắp xếp theo thời gian bắt đầu (phòng trường hợp file SRT không được sort)
        segments = sorted(segments, key=lambda x: x["start"])

        # Load video để lấy audio gốc và duration
        video = mp.VideoFileClip(str(video_path))
        orig_audio = video.audio
        video_duration = video.duration

        # Danh sách các audio clip sẽ được ghép theo thứ tự thời gian
        audio_parts = []
        current_time = 0.0

        # Xử lý từng segment
        for seg in segments:
            start = seg["start"]
            end = seg["end"]
            text = seg.get("text", "").strip()

            # 1. Phần audio gốc từ current_time đến start (nếu có gap)
            if start > current_time:
                gap_clip = orig_audio.subclipped(current_time, start)
                gap_clip = gap_clip.with_start(current_time)
                audio_parts.append(gap_clip)
                current_time = start

            # 2. Xử lý segment hiện tại
            if text:
                # Có text -> tạo TTS và thay thế hoàn toàn audio gốc trong khoảng này
                tts_clip = await self.tts_service.generate_smart_audio(
                    text=text,
                    start_time=start,
                    end_time=end,
                    index=seg.get("index", 0),
                    temp_dir=temp_dir
                )
                # generate_smart_audio đã set start_time = start, duration = end-start
                audio_parts.append(tts_clip)
            else:
                # Không có text -> giữ nguyên audio gốc
                orig_segment = orig_audio.subclipped(start, end)
                orig_segment = orig_segment.with_start(start)
                audio_parts.append(orig_segment)

            current_time = end

        # 3. Phần audio gốc còn lại sau segment cuối cùng
        if current_time < video_duration:
            tail_clip = orig_audio.subclipped(current_time, video_duration)
            tail_clip = tail_clip.with_start(current_time)
            audio_parts.append(tail_clip)

        # Ghép tất cả các audio part thành một track duy nhất
        final_audio = CompositeAudioClip(audio_parts)

        # Ghép audio với video (chạy trong thread để không block asyncio)
        loop = asyncio.get_event_loop()
        def _merge():
            final_video = video.with_audio(final_audio)
            final_video.write_videofile(
                str(output_path),
                codec="libx264",
                audio_codec="aac",
                logger=None
            )
            # Đóng video và audio gốc
            video.close()
            orig_audio.close()
            # Đóng các clip đã dùng (MoviePy tự giải phóng tài nguyên, nhưng gọi close để an toàn)
            for clip in audio_parts:
                clip.close()
            return output_path
        
        return await loop.run_in_executor(self.executor, _merge)