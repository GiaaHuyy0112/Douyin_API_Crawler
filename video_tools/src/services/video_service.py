import moviepy as mp
from pathlib import Path
from typing import List
import asyncio
from concurrent.futures import ThreadPoolExecutor
from src.services.tts_service import TTSService
from src.utils.srt_utils import parse_srt
from src.config import settings

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
        
        # Tạo audio clips cho từng segment (song song)
        tasks = []
        for i, seg in enumerate(segments):
            task = self.tts_service.generate_smart_audio(
                text=seg["text"],
                start_time=seg["start"],
                end_time=seg["end"],
                index=i,
                temp_dir=temp_dir
            )
            tasks.append(task)
        
        audio_clips = await asyncio.gather(*tasks)
        
        # Ghép audio và video (chạy trong thread)
        loop = asyncio.get_event_loop()
        def _merge():
            video = mp.VideoFileClip(str(video_path))
            final_audio = mp.CompositeAudioClip(audio_clips)
            final_video = video.with_audio(final_audio)
            final_video.write_videofile(
                str(output_path),
                codec="libx264",
                audio_codec="aac",
                logger=None
            )
            video.close()
            # Xoá file tạm audio
            for clip in audio_clips:
                if hasattr(clip, '_temp_audio_path'):
                    temp_path = clip._temp_audio_path
                    if temp_path.exists():
                        temp_path.unlink()
            return output_path
        
        return await loop.run_in_executor(self.executor, _merge)