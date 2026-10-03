from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import subprocess
import uuid
import os

app = FastAPI()

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.post("/merge-audio")
async def merge_audio(
    audio_files: list[UploadFile] = File(...)
):

    if len(audio_files) < 2:
        return {
            "error": "Please upload at least 2 audio files"
        }

    file_id = str(uuid.uuid4())

    input_files = []

    output_path = os.path.join(
        UPLOAD_FOLDER,
        f"{file_id}_merged.mp3"
    )

    try:

        # Save uploaded files

        for index, audio in enumerate(audio_files):

            input_path = os.path.join(
                UPLOAD_FOLDER,
                f"{file_id}_{index}_{audio.filename}"
            )

            with open(input_path, "wb") as buffer:

                while chunk := await audio.read(1024 * 1024):
                    buffer.write(chunk)

            input_files.append(input_path)

        # Create FFmpeg concat file

        concat_file = os.path.join(
            UPLOAD_FOLDER,
            f"{file_id}_concat.txt"
        )

        with open(concat_file, "w") as file:

            for input_file in input_files:

                absolute_path = os.path.abspath(input_file)

                # Escape single quotes for FFmpeg
                escaped_path = absolute_path.replace("'", "'\\''")

                file.write(
                    f"file '{escaped_path}'\n"
                )

        # Merge audio files

        subprocess.run(
            [
                "ffmpeg",

                "-f",
                "concat",

                "-safe",
                "0",

                "-i",
                concat_file,

                "-c:a",
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
            filename="merged-audio.mp3"
        )

    except subprocess.CalledProcessError:

        return {
            "error": "Audio merging failed"
        }

    finally:

        # Delete uploaded files

        for input_file in input_files:

            if os.path.exists(input_file):
                os.remove(input_file)

        # Delete concat file

        concat_file = os.path.join(
            UPLOAD_FOLDER,
            f"{file_id}_concat.txt"
        )

        if os.path.exists(concat_file):
            os.remove(concat_file)