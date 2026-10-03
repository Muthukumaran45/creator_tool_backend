from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
import subprocess
import uuid
import os

app = FastAPI()

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.post("/compress")
async def compress_video(
    video: UploadFile = File(...),
    quality: str = Form(...)
):

    # Validate compression level

    if quality not in ["low", "medium", "high"]:
        return {
            "error": "Invalid compression level"
        }

    # Generate unique ID

    file_id = str(uuid.uuid4())

    input_path = os.path.join(
        UPLOAD_FOLDER,
        f"{file_id}_{video.filename}"
    )

    output_path = os.path.join(
        UPLOAD_FOLDER,
        f"{file_id}_compressed.mp4"
    )

    # Save uploaded video

    with open(input_path, "wb") as buffer:

        while chunk := await video.read(1024 * 1024):
            buffer.write(chunk)

    # Select CRF based on quality

    if quality == "low":
        crf = "23"

    elif quality == "medium":
        crf = "28"

    else:
        crf = "32"

    try:

        subprocess.run(
            [
                "ffmpeg",

                "-i",
                input_path,

                "-c:v",
                "libx264",

                "-crf",
                crf,

                "-preset",
                "medium",

                "-c:a",
                "aac",

                "-b:a",
                "128k",

                "-movflags",
                "+faststart",

                output_path,
            ],
            check=True
        )

        return FileResponse(
            output_path,
            media_type="video/mp4",
            filename="compressed-video.mp4"
        )

    except subprocess.CalledProcessError:

        return {
            "error": "Video compression failed"
        }

    finally:

        # Delete uploaded original

        if os.path.exists(input_path):
            os.remove(input_path)