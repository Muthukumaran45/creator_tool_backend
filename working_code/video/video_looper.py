from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
import subprocess
import uuid
import os

app = FastAPI()

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.post("/loop")
async def loop_video(
    video: UploadFile = File(...),
    count: int = Form(...)
):

    # Validate count
    if count < 1 or count > 50:
        return {
            "error": "Loop count must be between 1 and 50"
        }

    # Generate unique ID
    file_id = str(uuid.uuid4())

    input_path = os.path.join(
        UPLOAD_FOLDER,
        f"{file_id}_{video.filename}"
    )

    output_path = os.path.join(
        UPLOAD_FOLDER,
        f"{file_id}_looped.mp4"
    )

    # Save uploaded video
    with open(input_path, "wb") as buffer:

        while chunk := await video.read(1024 * 1024):
            buffer.write(chunk)

    try:

        # Repeat video
        subprocess.run(
            [
                "ffmpeg",

                "-stream_loop",
                str(count - 1),

                "-i",
                input_path,

                "-c",
                "copy",

                output_path,
            ],
            check=True
        )

        return FileResponse(
            output_path,
            media_type="video/mp4",
            filename="looped-video.mp4"
        )

    except subprocess.CalledProcessError:

        return {
            "error": "Video processing failed"
        }

    finally:

        # Remove original uploaded video
        if os.path.exists(input_path):
            os.remove(input_path)