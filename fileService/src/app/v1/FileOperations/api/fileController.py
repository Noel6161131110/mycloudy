from fastapi import File, HTTPException, Depends, Request, Form
from fastapi.responses import StreamingResponse, JSONResponse
from sqlmodel import Session, select
from ..models.models import FileModel, Shares
from src.app.v1.Folders.models.models import Folders
from ..schemas import *
from src.database.db import getSession
from typing import List
from src.services.grpc_client import validateAccessToken
from uuid import uuid4, UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from src.dependencies.auth import getCurrentUserId
from src.security import security
import os, datetime, ffmpeg, random, string

def generate_upload_id():
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    rand_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{now}_{rand_str}"

async def testValidateToken(access_token: str):
    result = await validateAccessToken(access_token)
    
    if result['status'] == 'valid':
        return JSONResponse(
            content={"status": "valid", "userId": result['userId']},
            status_code=200
        )
    elif result['status'] == 'invalid':
        return JSONResponse(
            content={"status": "invalid", "userId": None},
            status_code=401
        )
    else:
        return JSONResponse(
            content={"status": "error", "userId": None},
            status_code=500
        )
    
async def get_video_duration(file_path: str) -> float:
    probe = ffmpeg.probe(file_path)
    return float(probe['format']['duration'])


async def getFiles(
    file_type: Optional[str] = None,
    userId: UUID = Depends(getCurrentUserId),
    db: AsyncSession = Depends(getSession)
    ):

    # Step 2: Get FileShares shared with the user
    file_share_query = await db.exec(
        select(Shares).where(Shares.sharedWithUserId == userId)
    )
    file_shares: List[Shares] = file_share_query.all()

    if not file_shares:
        return JSONResponse(content={"files": []}, status_code=200)

    # Step 3: Extract file IDs from FileShares
    file_ids = [share.fileId for share in file_shares]

    # Step 4: Build base query for Files
    query = select(FileModel).where(FileModel.id.in_(file_ids), FileModel.softDeleted == False)

    # Step 5: Filter by file_type if provided
    if file_type:
        if file_type not in ["video", "audio", "image", "document"]:
            raise HTTPException(status_code=400, detail="Invalid file type")
        query = query.where(FileModel.fileType == file_type)
    else:
        # If no file_type is provided, we can include all types
        query = query.where(FileModel.fileType.in_(["video", "audio", "image", "document"]))

    # Step 6: Execute final query
    result = await db.exec(query)
    files: List[FileModel] = result.all()

    # Step 7: Prepare response
    files_data = [
        {
            "id": str(file.id),
            "title": file.title,
            "description": file.description,
            "fileName": file.fileName,
            "fileExtension": file.fileExtension,
            "fileSize": file.fileSize,
            "filePath": file.filePath,
            "fileType": file.fileType,
            "lastModified": file.lastModified.isoformat(),
            "folderId": str(file.folderId),
            "tagId": str(file.tagId) if file.tagId else None,
            "totalVideoLength": file.totalVideoLength
        }
        for file in files
    ]

    return JSONResponse(content={"files": files_data}, status_code=200)
        



def getVideoInfo(file_id: int, db: Session = Depends(getSession)):
    video_file = db.get(FileModel, file_id)
    if not video_file:
        raise HTTPException(status_code=404, detail="Video file not found")
    
    return JSONResponse(content={"filename": video_file.filename, "total_length": video_file.total_length or "Not a video file", "currentTrackAt": video_file.current_track_at or 0}, status_code=200)

def streamVideo(file_id: int, request: Request, db: Session = Depends(getSession)):
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


def saveVideoTime(file_id: int, current_time: float, db: Session = Depends(getSession)):
    video_file = db.get(FileModel, file_id)
    if not video_file:
        raise HTTPException(status_code=404, detail="Video file not found")
    video_file.current_track_at = current_time
    video_file.last_updated_at = datetime.now()
    db.add(video_file)
    db.commit()
    
    return JSONResponse(content={"message": "Video time saved successfully!"}, status_code=200)


def showImage(file_id: int, db: Session = Depends(getSession)):
    image_file = db.get(FileModel, file_id)
    if not image_file:
        raise HTTPException(status_code=404, detail="Image file not found")
    return StreamingResponse(open(image_file.file_path, "rb"), media_type="image/jpeg")

def streamAudio(file_id: int, db: Session = Depends(getSession)):
    audio_file = db.get(FileModel, file_id)
    if not audio_file:
        raise HTTPException(status_code=404, detail="Audio file not found")
    return StreamingResponse(open(audio_file.file_path, "rb"), media_type="audio/mpeg")
