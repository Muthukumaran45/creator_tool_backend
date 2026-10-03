from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
import subprocess
import uuid
import os

app = FastAPI()

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.post("/convert-audio")
async def convert_audio(
    audio: UploadFile = File(...),
    format: str = Form(...)
):

    allowed_formats = [
        "mp3",
        "wav",
        "aac",
        "m4a",
        "flac"
    ]

    if format not in allowed_formats:
        return {
            "error": "Unsupported audio format"
        }

    file_id = str(uuid.uuid4())

    input_path = os.path.join(
        UPLOAD_FOLDER,
        f"{file_id}_{audio.filename}"
    )

    output_path = os.path.join(
        UPLOAD_FOLDER,
        f"{file_id}.{format}"
    )

    # Save uploaded audio

    with open(input_path, "wb") as buffer:

        while chunk := await audio.read(1024 * 1024):
            buffer.write(chunk)

    try:

        # FFmpeg command

        if format == "mp3":

            command = [
                "ffmpeg",
                "-i",
                input_path,
                "-vn",
                "-c:a",
                "libmp3lame",
                "-q:a",
                "2",
                output_path
            ]

        elif format == "wav":

            command = [
                "ffmpeg",
                "-i",
                input_path,
                "-vn",
                "-c:a",
                "pcm_s16le",
                output_path
            ]

        elif format == "aac":

            command = [
                "ffmpeg",
                "-i",
                input_path,
                "-vn",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                output_path
            ]

        elif format == "m4a":

            command = [
                "ffmpeg",
                "-i",
                input_path,
                "-vn",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                output_path
            ]

        elif format == "flac":

            command = [
                "ffmpeg",
                "-i",
                input_path,
                "-vn",
                "-c:a",
                "flac",
                output_path
            ]

        subprocess.run(
            command,
            check=True
        )

        return FileResponse(
            output_path,
            filename=f"converted-audio.{format}"
        )

    except subprocess.CalledProcessError:

        return {
            "error": "Audio conversion failed"
        }

    finally:

        # Delete original uploaded audio

        if os.path.exists(input_path):
            os.remove(input_path)