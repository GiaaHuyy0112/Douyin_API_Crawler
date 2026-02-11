import whisper
from pathlib import Path
from typing import Optional
import asyncio
from functools import lru_cache
from src.utils.srt_utils import format_timestamp

@lru_cache(maxsize=1)
def load_whisper_model(model_size: str = "base"):
    """Load model một lần, dùng cache"""
    return whisper.load_model(model_size)

async def generate_subtitles(video_path: Path, output_srt_path: Path, model_size: str = "base") -> Path:
    """
    Tạo file SRT từ video.
    Chạy whisper trong thread pool để không block event loop.
    """
    # Trích xuất audio tạm
    import tempfile
    import moviepy as mp
    
    loop = asyncio.get_event_loop()
    
    def _extract_audio_and_transcribe():
        # Tạo file tạm cho audio
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_audio:
            audio_path = Path(tmp_audio.name)
        
        try:
            video = mp.VideoFileClip(str(video_path))
            video.audio.write_audiofile(str(audio_path), logger=None)
            video.close()
            
            model = load_whisper_model(model_size)
            result = model.transcribe(str(audio_path), verbose=False, fp16=False)
            
            # Ghi SRT
            with open(output_srt_path, "w", encoding="utf-8") as f:
                for i, segment in enumerate(result["segments"]):
                    start = format_timestamp(segment["start"])
                    end = format_timestamp(segment["end"])
                    text = segment["text"].strip()
                    f.write(f"{i+1}\n{start} --> {end}\n{text}\n\n")
            
            return output_srt_path
        finally:
            # Xoá audio tạm
            if audio_path.exists():
                audio_path.unlink()
    
    return await loop.run_in_executor(None, _extract_audio_and_transcribe)