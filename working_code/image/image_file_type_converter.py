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
# IMAGE FILE TYPE CONVERTER
# =========================

@app.post("/convert-image")
async def convert_image(
    image: UploadFile = File(...),
    format: str = Form(...)
):

    allowed_formats = [
        "jpg",
        "png",
        "webp",
        "bmp",
        "tiff"
    ]

    format = format.lower()

    if format not in allowed_formats:
        return {
            "error": "Unsupported image format"
        }

    file_id = str(uuid.uuid4())

    input_path = os.path.join(
        UPLOAD_FOLDER,
        f"{file_id}_input"
    )

    output_path = os.path.join(
        UPLOAD_FOLDER,
        f"{file_id}_output.{format}"
    )

    try:

        # Save uploaded file
        with open(input_path, "wb") as buffer:

            while True:

                chunk = await image.read(1024 * 1024)

                if not chunk:
                    break

                buffer.write(chunk)


        # Open image
        with Image.open(input_path) as img:

            img = ImageOps.exif_transpose(img)


            # JPG
            if format == "jpg":

                if img.mode != "RGB":
                    img = img.convert("RGB")

                img.save(
                    output_path,
                    "JPEG",
                    quality=95,
                    optimize=True
                )

                media_type = "image/jpeg"


            # PNG
            elif format == "png":

                img.save(
                    output_path,
                    "PNG",
                    optimize=True
                )

                media_type = "image/png"


            # WEBP
            elif format == "webp":

                if img.mode not in ["RGB", "RGBA"]:
                    img = img.convert("RGBA")

                img.save(
                    output_path,
                    "WEBP",
                    quality=95,
                    method=6
                )

                media_type = "image/webp"


            # BMP
            elif format == "bmp":

                if img.mode != "RGB":
                    img = img.convert("RGB")

                img.save(
                    output_path,
                    "BMP"
                )

                media_type = "image/bmp"


            # TIFF
            elif format == "tiff":

                img.save(
                    output_path,
                    "TIFF"
                )

                media_type = "image/tiff"


        return FileResponse(
            output_path,
            media_type=media_type,
            filename=f"converted-image.{format}"
        )

    finally:

        if os.path.exists(input_path):
            os.remove(input_path)