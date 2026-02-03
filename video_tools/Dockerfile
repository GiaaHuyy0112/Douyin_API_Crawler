FROM python:3.11-slim

RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /app/video_tools

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src .

EXPOSE 9000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "9000"]