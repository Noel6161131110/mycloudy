from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Depends, Request
from sqlmodel import Session, select
from src.database.db import get_session
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import aiofiles
import os
import hashlib
from uuid import uuid4, UUID
from typing import Optional
import shutil
from pathlib import Path
import logging
from ..models.models import FileModel, FileShares
from src.app.v1.Folders.models.models import Folders
import ffmpeg
from datetime import datetime
from src.services.grpc_client import validateAccessToken

async def get_video_duration(file_path: str) -> float:
    probe = ffmpeg.probe(file_path)
    return float(probe['format']['duration'])

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Configuration
UPLOAD_DIR = Path("MYCLOUDY_VAULT")
TEMP_DIR = Path("temp_chunks")
MAX_FILE_SIZE = 5 * 1024 * 1024 * 1024  # 5GB
CHUNK_SIZE = 1024 * 1024  # 1MB chunks

ALLOWED_EXTENSIONS = {"mp4", "mov", "avi", "mkv", "webm", "mp3", "wav", "ogg", "flac", "jpg", "jpeg", "png"}

# Create directories if they don't exist
UPLOAD_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

class ChunkedUploadManager:
    def __init__(self):
        self.active_uploads = {}
    
    def start_upload(self, file_id: str, filename: str, total_size: int, metadata: dict = None):
        """Initialize a new chunked upload session"""
        if total_size > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail=f"File size exceeds maximum limit of {MAX_FILE_SIZE} bytes")
        
        chunk_dir = TEMP_DIR / file_id
        chunk_dir.mkdir(exist_ok=True)
        
        self.active_uploads[file_id] = {
            'filename': filename,
            'total_size': total_size,
            'chunk_dir': chunk_dir,
            'received_chunks': set(),
            'total_chunks': 0,
            'metadata': metadata or {}
        }
        
        return file_id
    
    async def upload_chunk(self, file_id: str, chunk_number: int, chunk_data: bytes):
        """Save a chunk to temporary storage"""
        if file_id not in self.active_uploads:
            raise HTTPException(status_code=404, detail="Upload session not found")
        
        upload_info = self.active_uploads[file_id]
        chunk_path = upload_info['chunk_dir'] / f"chunk_{chunk_number}"
        
        try:
            # Use a lock to prevent concurrent writes to the same file
            async with aiofiles.open(chunk_path, 'wb') as f:
                await f.write(chunk_data)
            
            upload_info['received_chunks'].add(chunk_number)
            upload_info['total_chunks'] = max(upload_info['total_chunks'], chunk_number + 1)
            
            logger.info(f"Uploaded chunk {chunk_number} for file {file_id}. Progress: {len(upload_info['received_chunks'])}/{upload_info['total_chunks']}")
            
            return len(upload_info['received_chunks'])
            
        except Exception as e:
            logger.error(f"Failed to save chunk {chunk_number} for file {file_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to save chunk: {str(e)}")
    
    async def finalize_upload(self, file_id: str, db: Session):
        """Combine all chunks into final file"""
        try:
            if file_id not in self.active_uploads:
                raise HTTPException(status_code=404, detail="Upload session not found")
            
            upload_info = self.active_uploads[file_id]
            metadata = upload_info.get('metadata', {})
            
            # Check if all chunks are received
            expected_chunks = set(range(upload_info['total_chunks']))
            if upload_info['received_chunks'] != expected_chunks:
                missing = expected_chunks - upload_info['received_chunks']
                print(f"Missing chunks: {sorted(missing)}")
                raise HTTPException(status_code=400, detail=f"Missing chunks: {sorted(missing)}")
            
            original_filename = upload_info['filename']
            file_ext = original_filename.split(".")[-1].lower()
            unique_filename = f"{uuid4()}_{original_filename}"
            final_path = UPLOAD_DIR / unique_filename
            
            async with aiofiles.open(final_path, 'wb') as final_file:
                for chunk_num in range(upload_info['total_chunks']):
                    chunk_path = upload_info['chunk_dir'] / f"chunk_{chunk_num}"
                    async with aiofiles.open(chunk_path, 'rb') as chunk_file:
                        chunk_data = await chunk_file.read()
                        await final_file.write(chunk_data)
            # Validate file extension
            if file_ext not in ALLOWED_EXTENSIONS:
                os.remove(final_path)
                raise HTTPException(status_code=400, detail="Invalid file type")

            # Determine file type and get additional metadata
            file_type = "unknown"
            total_length = None
            if file_ext in ["mp4", "mov", "avi", "mkv", "webm"]:
                file_type = "video"
                total_length = await get_video_duration(str(final_path))
            elif file_ext in ["mp3", "wav", "ogg", "flac"]:
                file_type = "audio"
            elif file_ext in ["jpg", "jpeg", "png"]:
                file_type = "image"

            final_title = metadata.get('title') or original_filename
            final_description = metadata.get('description') or ""

            # Save file metadata to DB
            new_file = FileModel(
                title=final_title,
                description=final_description,
                fileName=unique_filename,
                fileExtension=file_ext,
                fileSize=os.path.getsize(final_path),
                filePath=str(final_path),
                fileType=file_type,
                totalVideoLength=total_length,
                lastModified=datetime.now(),
                folderId=metadata.get('folderId'),
                tagId=metadata.get('tagId')
            )
            db.add(new_file)
            db.commit()
            db.refresh(new_file)

            # Create file share record
            file_share = FileShares(
                fileId=new_file.id,
                folderId=metadata.get('folderId'),
                sharedWithUserId=metadata.get('userId'),
                sharedByUserId=metadata.get('userId'),
                permission="owner",
                sharedAt=datetime.now()
            )
            db.add(file_share)
            db.commit()
            
            # Clean up temporary chunks
            shutil.rmtree(upload_info['chunk_dir'])
            del self.active_uploads[file_id]
            
            return {
                'id': new_file.id,
                'filename': original_filename,
                'title': final_title,
                'description': final_description,
                'file_type': file_type,
                'size': os.path.getsize(final_path),
                'path': str(final_path)
            }
        except Exception as e:
            print(f"Error finalizing upload for file {file_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to finalize upload: {str(e)}")

# Initialize upload manager
upload_manager = ChunkedUploadManager()


async def start_upload(
    request: Request,
    filename: str = Form(...), 
    total_size: int = Form(...),
    folderId: Optional[UUID] = Form(None),
    tagId: Optional[UUID] = Form(None),
    description: Optional[str] = Form(None),
    title: Optional[str] = Form(None),
    db: Session = Depends(get_session)
):
    """Start a new chunked upload session"""
    try:
        # Validate access token
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            print("Missing or invalid Authorization header")
            raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

        access_token = auth_header.split("Bearer ")[-1]
        result = await validateAccessToken(access_token)

        if result['status'] == 'valid':
            userId = result['userId']
        elif result['status'] == 'invalid':
            print("Invalid access token")
            raise HTTPException(status_code=401, detail="Invalid access token")
        else:
            print(f"Unexpected validation result: {result}")
            raise HTTPException(status_code=500, detail="Error validating access token")

        # Validate folder
        if not folderId:
            print("folderId is required")
            raise HTTPException(status_code=400, detail="folderId is required")

        folder = db.exec(select(Folders).where(Folders.id == folderId)).first()
        if not folder:
            print("Folder not found")
            raise HTTPException(status_code=404, detail="Folder not found")

        if folder.isSystem:
            if folder.createdBy is not None:
                raise HTTPException(status_code=403, detail="Cannot upload to system folder owned by another user")
        else:
            if not folder.createdBy:
                raise HTTPException(status_code=403, detail="Cannot upload to a folder without an owner")

        # Start upload session
        file_id = str(uuid4())
        upload_manager.start_upload(file_id, filename, total_size, {
            'userId': userId,
            'folderId': folderId,
            'tagId': tagId,
            'description': description,
            'title': title
        })
        
        return {"file_id": file_id, "chunk_size": CHUNK_SIZE}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")




async def upload_chunk(
    file_id: str = Form(...),
    chunk_number: int = Form(...),
    chunk: UploadFile = File(...)
):
    """Upload a single chunk"""
    try:
        # Add validation
        if chunk.size and chunk.size > CHUNK_SIZE * 2:  # Allow some buffer
            raise HTTPException(status_code=413, detail="Chunk size too large")
        
        chunk_data = await chunk.read()
        
        if not chunk_data:
            raise HTTPException(status_code=400, detail="Empty chunk received")
        
        chunks_received = await upload_manager.upload_chunk(file_id, chunk_number, chunk_data)
        
        return {
            "chunks_received": chunks_received,
            "chunk_number": chunk_number,
            "chunk_size": len(chunk_data)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading chunk {chunk_number} for file {file_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


async def finalize_upload(
    db: Session = Depends(get_session),
    file_id: str = Form(...)
    ):
    """Finalize the upload by combining all chunks"""
    try:
        result = await upload_manager.finalize_upload(file_id, db=db)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def get_upload_status(file_id: str):
    """Get the status of an ongoing upload"""
    if file_id not in upload_manager.active_uploads:
        raise HTTPException(status_code=404, detail="Upload session not found")
    
    upload_info = upload_manager.active_uploads[file_id]
    return {
        "filename": upload_info['filename'],
        "total_size": upload_info['total_size'],
        "chunks_received": len(upload_info['received_chunks']),
        "total_chunks": upload_info['total_chunks'],
        "progress": len(upload_info['received_chunks']) / max(upload_info['total_chunks'], 1) * 100
    }


async def get_upload_page():
    """Serve the HTML upload interface"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Chunked File Upload</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .upload-area { border: 2px dashed #ccc; padding: 40px; text-align: center; margin: 20px 0; }
            .upload-area.dragover { border-color: #007bff; background-color: #f0f8ff; }
            .progress-bar { width: 100%; height: 20px; background-color: #f0f0f0; border-radius: 10px; overflow: hidden; margin: 10px 0; }
            .progress-fill { height: 100%; background-color: #007bff; width: 0%; transition: width 0.3s ease; }
            .status { margin: 10px 0; padding: 10px; border-radius: 5px; }
            .status.success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
            .status.error { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
            .status.info { background-color: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
            button { padding: 10px 20px; margin: 5px; border: none; border-radius: 5px; cursor: pointer; }
            button:disabled { opacity: 0.5; cursor: not-allowed; }
            .primary { background-color: #007bff; color: white; }
            .secondary { background-color: #6c757d; color: white; }
            .upload-info { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 10px 0; }
            .upload-info div { padding: 5px; }
        </style>
    </head>
    <body>
        <h1>Chunked File Upload (Up to 5GB)</h1>
        
        <!-- Authentication Section -->
        <div style="margin-bottom: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 5px;">
            <h3>Authentication</h3>
            <input type="password" id="accessToken" placeholder="Enter access token" style="width: 100%; padding: 8px; margin-bottom: 10px;">
        </div>
        
        <!-- Upload Metadata Section -->
        <div style="margin-bottom: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 5px;">
            <h3>Upload Details</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                <div>
                    <label>Folder ID (Required):</label>
                    <input type="text" id="folderId" placeholder="Enter folder UUID" style="width: 100%; padding: 8px;">
                </div>
                <div>
                    <label>Tag ID (Optional):</label>
                    <input type="text" id="tagId" placeholder="Enter tag UUID" style="width: 100%; padding: 8px;">
                </div>
            </div>
            <div style="margin-top: 10px;">
                <label>Title (Optional):</label>
                <input type="text" id="title" placeholder="Custom title (defaults to filename)" style="width: 100%; padding: 8px; margin-bottom: 10px;">
            </div>
            <div>
                <label>Description (Optional):</label>
                <textarea id="description" placeholder="File description" style="width: 100%; padding: 8px; height: 60px; resize: vertical;"></textarea>
            </div>
        </div>
        
        <div class="upload-area" id="uploadArea">
            <p>Drag and drop files here or <button type="button" onclick="document.getElementById('fileInput').click()">Browse Files</button></p>
            <input type="file" id="fileInput" style="display: none;" multiple>
        </div>
        
        <div id="uploadStatus"></div>
        
        <script>
            const uploadArea = document.getElementById('uploadArea');
            const fileInput = document.getElementById('fileInput');
            const uploadStatus = document.getElementById('uploadStatus');
            const CHUNK_SIZE = 1024 * 1024; // 1MB chunks
            
            // Drag and drop handlers
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.classList.add('dragover');
            });
            
            uploadArea.addEventListener('dragleave', () => {
                uploadArea.classList.remove('dragover');
            });
            
            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('dragover');
                handleFiles(e.dataTransfer.files);
            });
            
            fileInput.addEventListener('change', (e) => {
                handleFiles(e.target.files);
            });
            
            function handleFiles(files) {
                // Validate required fields
                const accessToken = document.getElementById('accessToken').value.trim();
                const folderId = document.getElementById('folderId').value.trim();
                
                if (!accessToken) {
                    showStatus('Access token is required', 'error');
                    return;
                }
                
                if (!folderId) {
                    showStatus('Folder ID is required', 'error');
                    return;
                }
                
                Array.from(files).forEach(file => {
                    if (file.size > 5 * 1024 * 1024 * 1024) {
                        showStatus(`File ${file.name} exceeds 5GB limit`, 'error');
                        return;
                    }
                    uploadFile(file);
                });
            }
            
            function showStatus(message, type = 'info') {
                const statusDiv = document.createElement('div');
                statusDiv.className = `status ${type}`;
                statusDiv.textContent = message;
                uploadStatus.appendChild(statusDiv);
                
                // Remove status after 5 seconds for non-error messages
                if (type !== 'error') {
                    setTimeout(() => {
                        if (statusDiv.parentNode) {
                            statusDiv.parentNode.removeChild(statusDiv);
                        }
                    }, 5000);
                }
            }
            
            function formatBytes(bytes) {
                if (bytes === 0) return '0 Bytes';
                const k = 1024;
                const sizes = ['Bytes', 'KB', 'MB', 'GB'];
                const i = Math.floor(Math.log(bytes) / Math.log(k));
                return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
            }
            
            async function uploadFile(file) {
                const uploadId = Date.now() + '_' + Math.random().toString(36).substr(2, 9);
                
                // Create upload UI
                const uploadDiv = document.createElement('div');
                uploadDiv.id = `upload_${uploadId}`;
                uploadDiv.innerHTML = `
                    <h3>Uploading: ${file.name}</h3>
                    <div class="upload-info">
                        <div>Size: ${formatBytes(file.size)}</div>
                        <div>Status: <span id="status_${uploadId}">Starting...</span></div>
                        <div>Progress: <span id="progress_${uploadId}">0%</span></div>
                        <div>Speed: <span id="speed_${uploadId}">-</span></div>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" id="progressBar_${uploadId}"></div>
                    </div>
                    <button class="secondary" onclick="cancelUpload('${uploadId}')">Cancel</button>
                `;
                uploadStatus.appendChild(uploadDiv);
                
                try {
                    // Start upload session
                    const accessToken = document.getElementById('accessToken').value.trim();
                    const folderId = document.getElementById('folderId').value.trim();
                    const tagId = document.getElementById('tagId').value.trim();
                    const title = document.getElementById('title').value.trim();
                    const description = document.getElementById('description').value.trim();

                    const startFormData = new FormData();
                    startFormData.append('filename', file.name);
                    startFormData.append('total_size', file.size.toString());
                    startFormData.append('folderId', folderId);
                    if (tagId) startFormData.append('tagId', tagId);
                    if (title) startFormData.append('title', title);
                    if (description) startFormData.append('description', description);

                    const startResponse = await fetch('/api/v1/test-file-operations/upload/start', {
                        method: 'POST',
                        body: startFormData,
                        headers: {
                            'Authorization': `Bearer ${accessToken}`
                        }
                    });
                    
                    if (!startResponse.ok) {
                        throw new Error('Failed to start upload session');
                    }
                    
                    const { file_id, chunk_size } = await startResponse.json();
                    document.getElementById(`status_${uploadId}`).textContent = 'Uploading...';
                    
                    // Upload chunks
                    const totalChunks = Math.ceil(file.size / chunk_size);
                    let uploadedChunks = 0;
                    const startTime = Date.now();
                    
                    // Upload chunks with concurrency control and retry logic
                    const MAX_CONCURRENT_UPLOADS = 3;
                    const MAX_RETRIES = 3;
                    
                    async function uploadChunkWithRetry(chunkIndex, retryCount = 0) {
                        const start = chunkIndex * chunk_size;
                        const end = Math.min(start + chunk_size, file.size);
                        const chunk = file.slice(start, end);
                        
                        const formData = new FormData();
                        formData.append('file_id', file_id);
                        formData.append('chunk_number', chunkIndex.toString());
                        formData.append('chunk', chunk);
                        
                        try {
                            const response = await fetch('/api/v1/test-file-operations/upload/chunk', {
                                method: 'POST',
                                body: formData,
                                // Add timeout
                                signal: AbortSignal.timeout(30000) // 30 second timeout
                            });
                            
                            if (!response.ok) {
                                const errorText = await response.text();
                                throw new Error(`HTTP ${response.status}: ${errorText}`);
                            }
                            
                            uploadedChunks++;
                            const progress = (uploadedChunks / totalChunks) * 100;
                            const elapsed = Date.now() - startTime;
                            const speed = (uploadedChunks * chunk_size) / (elapsed / 1000);
                            
                            document.getElementById(`progress_${uploadId}`).textContent = `${progress.toFixed(1)}%`;
                            document.getElementById(`progressBar_${uploadId}`).style.width = `${progress}%`;
                            document.getElementById(`speed_${uploadId}`).textContent = formatBytes(speed) + '/s';
                            
                            return response.json();
                            
                        } catch (error) {
                            if (retryCount < MAX_RETRIES) {
                                console.log(`Retrying chunk ${chunkIndex}, attempt ${retryCount + 1}/${MAX_RETRIES}`);
                                await new Promise(resolve => setTimeout(resolve, 1000 * (retryCount + 1))); // Progressive delay
                                return uploadChunkWithRetry(chunkIndex, retryCount + 1);
                            } else {
                                console.error(`Failed to upload chunk ${chunkIndex} after ${MAX_RETRIES} retries:`, error);
                                throw new Error(`Chunk ${chunkIndex} failed: ${error.message}`);
                            }
                        }
                    }
                    
                    // Process chunks in batches to avoid overwhelming the server
                    const uploadPromises = [];
                    for (let i = 0; i < totalChunks; i += MAX_CONCURRENT_UPLOADS) {
                        const batch = [];
                        for (let j = i; j < Math.min(i + MAX_CONCURRENT_UPLOADS, totalChunks); j++) {
                            batch.push(uploadChunkWithRetry(j));
                        }
                        
                        // Wait for current batch to complete before starting next batch
                        await Promise.all(batch);
                        
                        // Small delay between batches to prevent overwhelming
                        await new Promise(resolve => setTimeout(resolve, 100));
                    }
                    
                    // Finalize upload
                    document.getElementById(`status_${uploadId}`).textContent = 'Finalizing...';
                    
                    const finalizeFormData = new FormData();
                    finalizeFormData.append('file_id', file_id);
                    
                    const finalizeResponse = await fetch('/api/v1/test-file-operations/upload/finalize', {
                        method: 'POST',
                        body: finalizeFormData
                    });
                    
                    if (!finalizeResponse.ok) {
                        throw new Error('Failed to finalize upload');
                    }
                    
                    const result = await finalizeResponse.json();
                    document.getElementById(`status_${uploadId}`).textContent = 'Complete!';
                    document.getElementById(`status_${uploadId}`).style.color = 'green';
                    
                    showStatus(`Successfully uploaded ${result.filename} (${formatBytes(result.size)})`, 'success');
                    
                } catch (error) {
                    document.getElementById(`status_${uploadId}`).textContent = 'Failed!';
                    document.getElementById(`status_${uploadId}`).style.color = 'red';
                    showStatus(`Error uploading ${file.name}: ${error.message}`, 'error');
                }
            }
            
            function cancelUpload(uploadId) {
                const uploadDiv = document.getElementById(`upload_${uploadId}`);
                if (uploadDiv) {
                    uploadDiv.remove();
                }
            }
        </script>
    </body>
    </html>
    """