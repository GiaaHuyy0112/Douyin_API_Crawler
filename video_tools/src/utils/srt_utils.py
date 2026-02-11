import re
from typing import List, Dict
import datetime

def format_timestamp(seconds: float) -> str:
    """Chuyển giây sang định dạng SRT: HH:MM:SS,mmm"""
    td = datetime.timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    millis = int(td.microseconds / 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

def srt_time_to_seconds(time_str: str) -> float:
    """Chuyển '00:00:10,000' -> 10.0"""
    time_str = time_str.replace(',', '.')
    parts = time_str.split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = float(parts[2])
    return hours * 3600 + minutes * 60 + seconds

def parse_srt(content: str) -> List[Dict]:
    """Phân tích nội dung file SRT thành list các segment: start, end, text"""
    blocks = re.split(r'\n\n', content.strip())
    segments = []
    for block in blocks:
        lines = block.split('\n')
        if len(lines) >= 3:
            # Dòng 2: timestamp
            time_range = lines[1]
            start_str, end_str = time_range.split(' --> ')
            start = srt_time_to_seconds(start_str)
            end = srt_time_to_seconds(end_str)
            text = " ".join(lines[2:]).strip()
            segments.append({
                "start": start,
                "end": end,
                "text": text
            })
    return segments