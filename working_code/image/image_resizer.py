from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from PIL import Image, ImageOps

import os
import uuid


# =========================
# APP
# =========================

app = FastAPI()


# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# UPLOAD FOLDER
# =========================

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =========================
# IMAGE RESIZER
# =========================

@app.post("/resize-image")
async def resize_image(
    image: UploadFile = File(...),
    width: str = Form(""),
    height: str = Form("")
):

    # Check dimensions
    target_width = int(width) if width else None
    target_height = int(height) if height else None

    if not target_width and not target_height:
        return {
            "error": "Enter width or height"
        }

    if target_width and target_width <= 0:
        return {
            "error": "Width must be greater than 0"
        }

    if target_height and target_height <= 0:
        return {
            "error": "Height must be greater than 0"
        }

    file_id = str(uuid.uuid4())

    input_path = os.path.join(
        UPLOAD_FOLDER,
        f"{file_id}_input"
    )

    output_path = os.path.join(
        UPLOAD_FOLDER,
        f"{file_id}_resized.jpg"
    )

    try:

        # =========================
        # SAVE UPLOADED IMAGE
        # =========================

        with open(input_path, "wb") as buffer:

            while True:

                chunk = await image.read(1024 * 1024)

                if not chunk:
                    break

                buffer.write(chunk)


        # =========================
        # OPEN IMAGE
        # =========================

        with Image.open(input_path) as img:

            # Fix phone camera orientation
            img = ImageOps.exif_transpose(img)

            original_width, original_height = img.size


            # =========================
            # WIDTH ONLY
            # =========================

            if target_width and not target_height:

                ratio = target_width / original_width

                target_height = int(
                    original_height * ratio
                )


            # =========================
            # HEIGHT ONLY
            # =========================

            elif target_height and not target_width:

                ratio = target_height / original_height

                target_width = int(
                    original_width * ratio
                )


            # =========================
            # RESIZE
            # =========================

            resized = img.resize(
                (target_width, target_height),
                Image.Resampling.LANCZOS
            )


            # JPEG needs RGB
            if resized.mode != "RGB":
                resized = resized.convert("RGB")


            # =========================
            # SAVE
            # =========================

            resized.save(
                output_path,
                "JPEG",
                quality=95,
                optimize=True
            )


        # =========================
        # RETURN FILE
        # =========================

        return FileResponse(
            output_path,
            media_type="image/jpeg",
            filename="resized-image.jpg"
        )


    finally:

        # Remove uploaded file
        if os.path.exists(input_path):
            os.remove(input_path)