from fastapi import UploadFile, File, HTTPException, Depends, Request, Form
from fastapi.responses import StreamingResponse, JSONResponse
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import FileTarget, ValueTarget
from streaming_form_data.validators import MaxSizeValidator
from starlette.requests import ClientDisconnect
from sqlmodel import Session, select
import os, datetime
import aiofiles
import ffmpeg
from ..models.models import FileModel, FileShares
from src.app.v1.Folders.models.models import Folders
from ..schemas import *
from src.database.db import get_session
import shutil
from src.services.grpc_client import validateAccessToken
from uuid import uuid4, UUID

import random, string


CHUNK_DIR = "chunks"
FINAL_DIR = "MYCLOUDY_VAULT"
ALLOWED_EXTENSIONS = ["mp4", "mov", "avi", "mkv", "webm", "mp3", "wav", "ogg", "flac", "jpg", "jpeg", "png"]
MAX_CHUNK_SIZE = 1024 * 1024 * 1024 * 5

def generate_upload_id():
    now = datetime.utcnow().strftime("%Y%m%d%H%M%S")
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


async def uploadFileAsChunk(
    request: Request,
    chunkNumber: int = Form(...),
    totalChunks: int = Form(...),
    uploadSessionId: Optional[str] = Form(None),
    folderId: Optional[UUID] = Form(None),
    tagId: Optional[UUID] = Form(None),
    description: Optional[str] = Form(None),
    title: Optional[str] = Form(None),
    db: Session = Depends(get_session)
):
    try:
        chunkNumber = int(chunkNumber)
        totalChunks = int(totalChunks)
        upload_session_id = uploadSessionId or generate_upload_id()

        # Validate token & folder only for chunk 1 or last chunk
        userId = None
        if chunkNumber in (1, totalChunks):
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

            access_token = auth_header.split("Bearer ")[-1]
            result = await validateAccessToken(access_token)

            if result['status'] == 'valid':
                userId = result['userId']
            elif result['status'] == 'invalid':
                raise HTTPException(status_code=401, detail="Invalid access token")
            else:
                raise HTTPException(status_code=500, detail="Error validating access token")

            if not folderId:
                raise HTTPException(status_code=400, detail="folderId is required")

            folder = db.exec(select(Folders).where(Folders.id == folderId)).first()
            if not folder:
                raise HTTPException(status_code=404, detail="Folder not found")

            if folder.isSystem:
                if folder.createdBy is not None:
                    raise HTTPException(status_code=403, detail="Cannot upload to system folder owned by another user")
            else:
                if not folder.createdBy:
                    raise HTTPException(status_code=403, detail="Cannot upload to a folder without an owner")

        # Save chunk
        chunkFolder = os.path.join(CHUNK_DIR, upload_session_id)
        os.makedirs(chunkFolder, exist_ok=True)
        chunkPath = os.path.join(chunkFolder, f"chunk_{chunkNumber}")

        file_target = FileTarget(chunkPath, validator=MaxSizeValidator(MAX_CHUNK_SIZE))
        parser = StreamingFormDataParser(headers=request.headers)
        parser.register("file", file_target)

        try:
            async for chunk in request.stream():
                parser.data_received(chunk)
        except ClientDisconnect:
            raise HTTPException(status_code=499, detail="Client disconnected")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error receiving file chunk: {str(e)}")

        if not file_target.multipart_filename:
            raise HTTPException(status_code=422, detail="File is missing or invalid")

        print(f"[Chunk {chunkNumber}] Written to {chunkPath}")

        # If final chunk, merge all
        if chunkNumber == totalChunks:
            print("🔧 Final chunk received. Starting merge process.")
            finalFileName = f"{uuid4()}_{file_target.multipart_filename}"
            finalPath = os.path.join(FINAL_DIR, finalFileName)
            os.makedirs(FINAL_DIR, exist_ok=True)

            try:
                with open(finalPath, "wb") as dest:
                    for i in range(1, totalChunks + 1):
                        chunkFile = os.path.join(chunkFolder, f"chunk_{i}")
                        if not os.path.exists(chunkFile):
                            raise HTTPException(status_code=400, detail=f"Missing chunk {i}")
                        with open(chunkFile, "rb") as src:
                            shutil.copyfileobj(src, dest)
                        os.remove(chunkFile)
                os.rmdir(chunkFolder)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error merging chunks: {str(e)}")

            # File type determination
            fileExt = file_target.multipart_filename.split(".")[-1].lower()
            if fileExt not in ALLOWED_EXTENSIONS:
                os.remove(finalPath)
                raise HTTPException(status_code=400, detail="Invalid file type")

            fileType = "unknown"
            totalLength = None
            if fileExt in ["mp4", "mov", "avi", "mkv", "webm"]:
                fileType = "video"
                totalLength = await get_video_duration(finalPath)
            elif fileExt in ["mp3", "wav", "ogg", "flac"]:
                fileType = "audio"
            elif fileExt in ["jpg", "jpeg", "png"]:
                fileType = "image"

            finalTitle = title or file_target.multipart_filename
            finalDescription = description or ""

            # Save file metadata to DB
            newFile = FileModel(
                title=finalTitle,
                description=finalDescription,
                fileName=finalFileName,
                fileExtension=fileExt,
                fileSize=os.path.getsize(finalPath),
                filePath=finalPath,
                fileType=fileType,
                totalVideoLength=totalLength,
                lastModified=datetime.utcnow(),
                folderId=folderId,
                tagId=tagId
            )
            db.add(newFile)
            db.commit()
            db.refresh(newFile)

            fileShare = FileShares(
                fileId=newFile.id,
                folderId=folderId,
                sharedWithUserId=userId,
                sharedByUserId=userId,
                permission="owner",
                sharedAt=datetime.utcnow()
            )
            db.add(fileShare)
            db.commit()

            print(f"✅ File {finalFileName} uploaded and saved by user {userId}")

            return JSONResponse(
                content={
                    "message": "File uploaded successfully!",
                    "fileName": finalFileName,
                    "totalLength": totalLength or "N/A"
                },
                status_code=201
            )

        return JSONResponse(
            content={
                "message": f"Chunk {chunkNumber}/{totalChunks} uploaded.",
                "uploadId": upload_session_id
            },
            status_code=200
        )

    except HTTPException as e:
        print(f"HTTP Exception: {e.detail}")
        return JSONResponse(content={"detail": e.detail}, status_code=e.status_code)

    except Exception as e:
        print(f"Error in uploadFileAsChunk: {str(e)}")
        return JSONResponse(
            content={"detail": "Internal server error"},
            status_code=500
        )
        

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
