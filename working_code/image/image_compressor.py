from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from PIL import Image, ImageOps

import os
import uuid


app = FastAPI()

# -------------------------
# CORS
# -------------------------

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


# -------------------------
# Upload folder
# -------------------------

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# -------------------------
# Image Compressor
# -------------------------

@app.post("/compress-image")
async def compress_image(
    image: UploadFile = File(...),
    quality: str = Form(...)
):

    # Validate quality
    if quality not in ["low", "medium", "high"]:
        return {
            "error": "Quality must be low, medium, or high"
        }

    file_id = str(uuid.uuid4())

    input_path = os.path.join(
        UPLOAD_FOLDER,
        f"{file_id}_input"
    )

    # Save uploaded image
    with open(input_path, "wb") as buffer:

        while True:
            chunk = await image.read(1024 * 1024)

            if not chunk:
                break

            buffer.write(chunk)

    output_path = None

    try:

        # Quality values
        quality_values = {
            "high": 85,
            "medium": 65,
            "low": 45,
        }

        compression_quality = quality_values[quality]

        # Open image
        with Image.open(input_path) as img:

            # Fix phone camera orientation
            img = ImageOps.exif_transpose(img)

            original_format = img.format

            # -------------------------
            # PNG
            # -------------------------

            if original_format == "PNG":

                output_path = os.path.join(
                    UPLOAD_FOLDER,
                    f"{file_id}_compressed.png"
                )

                img.save(
                    output_path,
                    format="PNG",
                    optimize=True,
                    compress_level=9
                )

                media_type = "image/png"
                filename = "compressed-image.png"

            # -------------------------
            # WEBP
            # -------------------------

            elif original_format == "WEBP":

                output_path = os.path.join(
                    UPLOAD_FOLDER,
                    f"{file_id}_compressed.webp"
                )

                img.save(
                    output_path,
                    format="WEBP",
                    quality=compression_quality,
                    method=6
                )

                media_type = "image/webp"
                filename = "compressed-image.webp"

            # -------------------------
            # JPEG / JPG / Other
            # -------------------------

            else:

                output_path = os.path.join(
                    UPLOAD_FOLDER,
                    f"{file_id}_compressed.jpg"
                )

                # Convert to RGB
                if img.mode != "RGB":
                    img = img.convert("RGB")

                img.save(
                    output_path,
                    format="JPEG",
                    quality=compression_quality,
                    optimize=True,
                    progressive=True
                )

                media_type = "image/jpeg"
                filename = "compressed-image.jpg"

        # Return compressed image
        return FileResponse(
            output_path,
            media_type=media_type,
            filename=filename
        )

    finally:

        # Remove original upload
        if os.path.exists(input_path):
            os.remove(input_path)