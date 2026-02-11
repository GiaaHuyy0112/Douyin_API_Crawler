import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # Có thể ghi đè bằng biến môi trường
    whisper_model_size: str = Field("base", env="WHISPER_MODEL_SIZE")
    tts_voice: str = Field("vi-VN-HoaiMyNeural", env="TTS_VOICE")
    tts_rate: str = Field("+0%", env="TTS_RATE")  # mặc định, sẽ điều chỉnh động
    max_speed_increase_percent: int = Field(50, env="MAX_SPEED_INCREASE_PERCENT")
    
    # Thư mục làm việc
    downloads_dir: Path = Field(Path("/home/shared/downloads"), env="DOWNLOADS_DIR")
    srt_dir: Path = Field(Path("/home/shared/srt"), env="SRT_DIR")
    export_dir: Path = Field(Path("/home/shared/export"), env="EXPORT_DIR")
    temp_dir: Path = Field(Path("/tmp/dubbing_app"), env="TEMP_DIR")
    
    # FastAPI
    api_host: str = Field("0.0.0.0", env="API_HOST")
    api_port: int = Field(9000, env="API_PORT")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()