from fastapi import UploadFile, File, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse, JSONResponse
from sqlmodel import Session, select
import os, datetime
import aiofiles
import ffmpeg
from ..models.models import FileModel
from ..schemas import *
from src.database.db import get_session

async def get_video_duration(file_path: str) -> float:
    probe = ffmpeg.probe(file_path)
    return float(probe['format']['duration'])


async def uploadFile(file: UploadFile = File(...), title: str = None, db: Session = Depends(get_session)):
    if not title:
        raise HTTPException(status_code=400, detail="Title is required")
    
    file_ext = file.filename.split(".")[-1]
    file_path = f"storage/{file.filename}"
    os.makedirs("storage", exist_ok=True)
    
    async with aiofiles.open(file_path, "wb") as buffer:
        while content := await file.read(1024):
            await buffer.write(content)
    
    file_type = "unknown"
    if file_ext in ["mp4", "mov", "avi", "mkv", "webm"]:
        file_type = "video"
        total_length = await get_video_duration(file_path)
    elif file_ext in ["mp3", "wav", "ogg", "flac"]:
        file_type = "audio"
        total_length = None
    elif file_ext in ["jpg", "jpeg", "png"]:
        file_type = "image"
        total_length = None
    else:
        raise HTTPException(status_code=400, detail="Invalid file type")

    new_file = FileModel(title=title, filename=file.filename, fileExtension=file_ext, filePath=file_path, fileType=file_type, totalVideoLength=total_length)
    db.add(new_file)
    db.commit()
    
    return JSONResponse(content={"message": "File uploaded successfully!", "file_name": file.filename, "total_length": total_length or "Not a video file"}, status_code=201)

def getFiles(file_type: str, db: Session = Depends(get_session)):
    if file_type not in ["video", "audio", "image"]:
        raise HTTPException(status_code=400, detail="Invalid file type")

    files = db.exec(select(FileModel).where(FileModel.fileType == file_type)).all()

    files_data = [
        {
            **file.dict(),
            "uploadedAt": file.uploadedAt.isoformat() if file.uploadedAt else None,
            "lastUpdatedAt": file.lastUpdatedAt.isoformat() if file.lastUpdatedAt else None
        }
        for file in files
    ]

    return JSONResponse(content={"files": files_data}, status_code=200)


def getVideoInfo(file_id: int, db: Session = Depends(get_session)):
    video_file = db.get(FileModel, file_id)
    if not video_file:
        raise HTTPException(status_code=404, detail="Video file not found")
    
    return JSONResponse(content={"filename": video_file.filename, "total_length": video_file.total_length or "Not a video file", "currentTrackAt": video_file.current_track_at or 0}, status_code=200)

def streamVideo(file_id: int, request: Request, db: Session = Depends(get_session)):
    video_file = db.get(FileModel, file_id)
    if not video_file:
        raise HTTPException(status_code=404, detail="Video file not found")
    
    file_path = video_file.file_path
    file_size = os.path.getsize(file_path)
    chunk_size = 1024 * 1024  # 1MB chunks

    range_header = request.headers.get("range")
    start = 0
    end = file_size - 1

    if range_header:
        range_values = range_header.replace("bytes=", "").split("-")
        start = int(range_values[0]) if range_values[0] else 0
        end = int(range_values[1]) if len(range_values) > 1 and range_values[1] else end

    end = min(end, file_size - 1)  # Ensure end is within bounds

    def file_iterator(start_pos, end_pos):
        with open(file_path, "rb") as f:
            f.seek(start_pos)
            while start_pos <= end_pos:
                data = f.read(min(chunk_size, end_pos - start_pos + 1))
                if not data:
                    break
                yield data
                start_pos += len(data)

    return StreamingResponse(
        file_iterator(start, end),
        status_code=206,
        headers={
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(end - start + 1),
            "Content-Type": "video/mp4",
        },
    )


def saveVideoTime(file_id: int, current_time: float, db: Session = Depends(get_session)):
    video_file = db.get(FileModel, file_id)
    if not video_file:
        raise HTTPException(status_code=404, detail="Video file not found")
    video_file.current_track_at = current_time
    video_file.last_updated_at = datetime.now()
    db.add(video_file)
    db.commit()
    
    return JSONResponse(content={"message": "Video time saved successfully!"}, status_code=200)


def showImage(file_id: int, db: Session = Depends(get_session)):
    image_file = db.get(FileModel, file_id)
    if not image_file:
        raise HTTPException(status_code=404, detail="Image file not found")
    return StreamingResponse(open(image_file.file_path, "rb"), media_type="image/jpeg")

def streamAudio(file_id: int, db: Session = Depends(get_session)):
    audio_file = db.get(FileModel, file_id)
    if not audio_file:
        raise HTTPException(status_code=404, detail="Audio file not found")
    return StreamingResponse(open(audio_file.file_path, "rb"), media_type="audio/mpeg")
