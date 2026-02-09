import os
import whisper
from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip
import datetime
from fastapi import FastAPI
import asyncio
import edge_tts
import re

app = FastAPI()

def format_timestamp(seconds: float):
    """Chuyển đổi giây thành định dạng thời gian SRT: HH:MM:SS,mmm"""
    td = datetime.timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    millis = int(td.microseconds / 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

def generate_subtitles(name: str):
    try:
        print("--- Đang trích xuất âm thanh từ video... ---")
        video = VideoFileClip(f"/home/shared/downloads/{name}.mp4")
        output_srt = f"/home/shared/srt/{name}.srt"
        audio_path = f"/home/shared/temp/{name}.mp3"
        video.audio.write_audiofile(audio_path, logger=None)
        
        print("--- Đang nhận diện giọng nói (Whisper)... ---")
        model = whisper.load_model("base")
        result = model.transcribe(audio_path, verbose=False, fp16=False)

        # Bước 3: Ghi dữ liệu ra file .srt
        print(f"--- Đang tạo file phụ đề: {output_srt} ---")
        with open(output_srt, "w", encoding="utf-8") as f:
            for i, segment in enumerate(result['segments']):
                start = format_timestamp(segment['start'])
                end = format_timestamp(segment['end'])
                text = segment['text'].strip()
                
                f.write(f"{i + 1}\n")
                f.write(f"{start} --> {end}\n")
                f.write(f"{text}\n\n")

        print(f"✅ THÀNH CÔNG! File của bạn nằm tại: {os.path.abspath(output_srt)}")
        return {"message": "Subtitles created successfully", "srt_path": os.path.abspath(output_srt)}
    except Exception as e:
        print(f"❌ Có lỗi xảy ra: {e}")
        return {"error": str(e)}
    finally:
        # Dọn dẹp file tạm
        if os.path.exists(audio_path):
            os.remove(audio_path)
            
# Cấu hình giọng đọc (vi-VN-HoaiMyNeural hoặc vi-VN-NamMinhNeural)

def srt_time_to_seconds(time_str):
    """Chuyển định dạng 00:00:10,000 thành giây (float)"""
    hours, minutes, seconds = time_str.replace(',', '.').split(':')
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)

async def generate_audio_segments(srt_path):
    """Tạo các đoạn audio nhỏ từ file SRT"""
    with open(srt_path, 'r', encoding='utf-8') as f:
        content = f.read()

    blocks = re.split(r'\n\n', content.strip())
    audio_clips = []
    
    print(f"--- Đang tạo giọng nói cho {len(blocks)} đoạn... ---")
    
    i = 0
    for block in blocks:
        print("Tiến trình:", round(i / len(blocks) * 100, 2), "%")
        lines = block.split('\n')
        if len(lines) >= 3:
            time_range = lines[1]
            start_str, end_str = time_range.split(' --> ')
            start_time = srt_time_to_seconds(start_str)
            text = " ".join(lines[2:])
            
            # Tạo file audio tạm cho đoạn này
            temp_mp3 = f"/home/shared/temp/temp_{start_time}.mp3"
            VOICE = "vi-VN-HoaiMyNeural"
            communicate = edge_tts.Communicate(text, VOICE)
            await communicate.save(temp_mp3)
            
            # Tạo Audio Clip và đặt mốc thời gian bắt đầu
            audio_clip = AudioFileClip(temp_mp3).with_start(start_time)
            audio_clips.append(audio_clip)
            i += 1
            
    return audio_clips

async def generate_smart_audio(text, start_time, end_time, index):
    limit = end_time - start_time
    temp_mp3 = f"/home/shared/temp/segment_{index}.mp3"
    
    VOICE = "vi-VN-HoaiMyNeural"
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(temp_mp3)
    
    actual_duration = AudioFileClip(temp_mp3).duration
    
    if actual_duration > limit:
        speed_increase = min(int(((actual_duration / limit) - 1) * 100), 50)
        rate_str = f"+{speed_increase}%"
        print(f"⚠️ Đoạn {index} quá dài ({actual_duration:.2f}s > {limit:.2f}s). Tăng tốc: {rate_str}")
        
        communicate = edge_tts.Communicate(text, VOICE, rate=rate_str)
        await communicate.save(temp_mp3)
    
    return AudioFileClip(temp_mp3).with_start(start_time)

def srt_time_to_seconds(time_str):
    hours, minutes, seconds = time_str.replace(',', '.').split(':')
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)

async def process_dubbing(video_path, srt_path, output_path):
    with open(srt_path, 'r', encoding='utf-8') as f:
        content = f.read()

    blocks = re.split(r'\n\n', content.strip())
    audio_clips = []

    for i, block in enumerate(blocks):
        print("Tiến trình:", round(i / len(blocks) * 100, 2), "%")
        lines = block.split('\n')
        if len(lines) >= 3:
            time_range = lines[1]
            start_str, end_str = time_range.split(' --> ')
            start_time = srt_time_to_seconds(start_str)
            end_time = srt_time_to_seconds(end_str)
            text = " ".join(lines[2:])
            
            clip = await generate_smart_audio(text, start_time, end_time, i)
            audio_clips.append(clip)

    # Ghép vào video
    video = VideoFileClip(video_path)
    final_audio = CompositeAudioClip(audio_clips)
    
    # Giữ lại 10% âm thanh gốc để làm tiếng động nền (Ambient sound)
    # Hoặc video.audio.volumex(0.1)
    final_video = video.with_audio(final_audio)
    final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")

def merge_audio_to_video(video_path, audio_clips, output_path):
    """Ghép tất cả audio vào video gốc"""
    print("--- Đang trộn âm thanh và xuất video... ---")
    video = VideoFileClip(video_path)
    
    # Trộn các đoạn audio lại với nhau
    final_audio = CompositeAudioClip(audio_clips)
    
    # Giảm âm lượng video gốc xuống (hoặc tắt hẳn bằng cách không dùng video.audio)
    # Ở đây tôi sẽ tắt hẳn âm thanh gốc để nghe rõ giọng lồng tiếng
    final_video = video.with_audio(final_audio)
    
    final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
    print(f"✅ HOÀN TẤT! Video lồng tiếng: {output_path}")
    
    
@app.get("/generate_subtitles")
async def create_subtitles_endpoint(name: str = None):
    try:
        if not name:
            raise ValueError("name is required")
        return generate_subtitles(name)
    except Exception as e:
        return {"error": str(e)}
    
    
@app.get("/generate_dubbed_video")
async def create_dubbed_video_endpoint(name: str = None):
    try:
        if not name:
            raise ValueError("name is required")
        # Tạo video lồng tiếng
        srt_path = f"/home/shared/srt/{name}.srt"
        output_video = f"/home/shared/export/{name}_dubbed.mp4"
        
        audio_clips = await generate_audio_segments(srt_path)
        merge_audio_to_video(f"/home/shared/import/{name}.mp4", audio_clips, output_video)
        
        return {"message": "Dubbed video created successfully", "video_path": output_video}
    except Exception as e:
        return {"error": str(e)}
    
    
@app.get("/generate_final_video")
async def create_final_video(name: str = None):
    try:
        if not name:
            raise ValueError("name is required")
        
        org_path = f"/home/shared/downloads/{name}.mp4"
        srt_path = f"/home/shared/srt/{name}.srt"
        output_video = f"/home/shared/export/{name}_final.mp4"
        
        await process_dubbing(org_path, srt_path, output_video)
        
        return {"message": "Final video created successfully", "video_path": output_video}
    except Exception as e:
        return {"error": str(e)}