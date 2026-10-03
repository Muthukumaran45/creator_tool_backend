from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import subprocess
import uuid
import os

app = FastAPI()

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.post("/convert")
async def convert_video(video: UploadFile = File(...)):

    # Create unique filenames
    file_id = str(uuid.uuid4())

    video_path = os.path.join(
        UPLOAD_FOLDER,
        f"{file_id}_{video.filename}"
    )

    audio_path = os.path.join(
        UPLOAD_FOLDER,
        f"{file_id}.mp3"
    )

    # Save uploaded video
    with open(video_path, "wb") as buffer:
        while chunk := await video.read(1024 * 1024):
            buffer.write(chunk)

    # Convert video → MP3
    subprocess.run(
        [
            "ffmpeg",
            "-i",
            video_path,
            "-vn",
            "-acodec",
            "libmp3lame",
            "-q:a",
            "2",
            audio_path,
        ],
        check=True,
    )

    # Delete original video
    os.remove(video_path)

    # Return MP3
    return FileResponse(
        audio_path,
        media_type="audio/mpeg",
        filename="audio.mp3",
    )