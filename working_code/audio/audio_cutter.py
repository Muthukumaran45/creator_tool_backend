from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
import subprocess
import uuid
import os

app = FastAPI()

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.post("/cut-audio")
async def cut_audio(
    audio: UploadFile = File(...),
    start_time: str = Form(...),
    end_time: str = Form(...)
):

    file_id = str(uuid.uuid4())

    input_path = os.path.join(
        UPLOAD_FOLDER,
        f"{file_id}_{audio.filename}"
    )

    output_path = os.path.join(
        UPLOAD_FOLDER,
        f"{file_id}_cut.mp3"
    )

    # Save uploaded audio

    with open(input_path, "wb") as buffer:

        while chunk := await audio.read(1024 * 1024):
            buffer.write(chunk)

    try:

        # Cut audio using FFmpeg

        subprocess.run(
            [
                "ffmpeg",

                "-i",
                input_path,

                "-ss",
                start_time,

                "-to",
                end_time,

                "-vn",

                "-acodec",
                "libmp3lame",

                "-q:a",
                "2",

                output_path,
            ],
            check=True
        )

        return FileResponse(
            output_path,
            media_type="audio/mpeg",
            filename="cut-audio.mp3"
        )

    except subprocess.CalledProcessError:

        return {
            "error": "Audio cutting failed"
        }

    finally:

        # Delete original uploaded file

        if os.path.exists(input_path):
            os.remove(input_path)