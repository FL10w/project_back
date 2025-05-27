from fastapi import UploadFile, HTTPException
from pathlib import Path
import os
from app.core.config import settings


async def save_profile_picture(user_id: int, file: UploadFile):
    upload_dir = Path(settings.UPLOADS_DIR) / "profile_pictures"
    upload_dir.mkdir(exist_ok=True)

    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(
            status_code=400,
            detail="Only JPEG and PNG images are allowed"
        )

    filename = f"{user_id}.jpg"
    file_path = upload_dir / filename

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    return filename