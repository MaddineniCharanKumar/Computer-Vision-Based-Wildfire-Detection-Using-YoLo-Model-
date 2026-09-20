from __future__ import annotations

from fastapi import APIRouter, File, UploadFile

router = APIRouter()


@router.post("/detection/image")
async def detection_image(file: UploadFile = File(...)) -> dict:
    return {
        "status": "accepted",
        "filename": file.filename,
        "message": "Detection request accepted.",
    }


@router.post("/detection/video")
async def detection_video() -> dict:
    return {
        "status": "accepted",
        "message": "Video detection pipeline is ready for integration.",
    }
