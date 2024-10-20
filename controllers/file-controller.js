import 'dotenv/config';
import fs from "fs";
import { FileModel } from '../models/file-model.js';
import { getRepository } from 'typeorm';
import path from 'path';
import { AppDataSource } from '../db/data-source.js';
import pkg from 'fluent-ffmpeg';
const { ffprobe } = pkg;
const fileController = {};

const getVideoDuration = (filePath) => {
  return new Promise((resolve, reject) => {
    ffprobe(filePath, (err, metadata) => {
      if (err) {
        return reject(err);
      }
      // The duration is in seconds
      const duration = metadata.format.duration;
      resolve(duration);
    });
  });
};


// * Function to upload files
fileController.UploadFile = async (req, res) => {
  if (!req.file) {
    return res.status(400).send('No file uploaded.');
  }

  try {
    const { filename, path: filePath } = req.file;
    const fileExtension = filename.split('.').pop();
    const fullFilePath = path.join(process.cwd(), filePath);

    console.log('File details:', fullFilePath, fileExtension);

    let totalLength = null;

    // Check if the file is a video by its extension
    const videoExtensions = ['mp4', 'mov', 'avi', 'mkv', 'webm'];
    if (videoExtensions.includes(fileExtension.toLowerCase())) {
      // Use ffmpeg to get the video duration
      totalLength = await getVideoDuration(fullFilePath);
      console.log('Video duration:', totalLength);
    }

    // Use the repository pattern to create and save the file details
    const fileRepository = AppDataSource.getRepository('FileModel'); // Ensure 'FileModel' matches your entity
    const fileDetails = fileRepository.create({
      filename,
      fileExtension,
      filePath: fullFilePath,
      totalLength, // Store the total length of the video if available
    });

    await fileRepository.save(fileDetails); // Save to the database

    return res.send({
      message: 'File uploaded successfully!',
      fileName: filename,
      totalLength: totalLength || 'Not a video file',
    });
  } catch (error) {
    console.error('Error saving file details:', error);
    return res.status(500).send('An error occurred while uploading the file.');
  }
};

// * Function to stream video
fileController.StreamVideo = async (req, res) => {
  const range = req.headers.range;
  
  const fileId = req.query.id;
  console.log('Video ID:', fileId);
  if (!fileId) {
    return res.status(400).send("Missing video ID query parameter");
  }

  const fileRepository = AppDataSource.getRepository(FileModel);
  const videoFile = await fileRepository.findOne({ where: { id: fileId } });

  if (!videoFile) {
    return res.status(404).send("Video file not found");
  }

  const videoPath = videoFile.filePath;
  const currentTrackAt = videoFile.currentTrackAt || 0;


  const videoSize = fs.statSync(videoPath).size;
  const CHUNK_SIZE = 10 ** 6; // 1MB per chunk


  let start;
  if (range) {
    // If Range header exists, use it to calculate start
    start = Number(range.replace(/\D/g, ""));
  } else {
    start = Math.floor((currentTrackAt / 100) * videoSize);
  }
  const end = Math.min(start + CHUNK_SIZE - 1, videoSize - 1);

  // Create response headers
  const contentLength = end - start + 1;
  const headers = {
    "Content-Range": `bytes ${start}-${end}/${videoSize}`,
    "Accept-Ranges": "bytes",
    "Content-Length": contentLength,
    "Content-Type": "video/mp4",
  };

  res.writeHead(206, headers);

  const videoStream = fs.createReadStream(videoPath, { start, end });
  videoStream.pipe(res);

  const videoDuration = 100; 
  let elapsedTime = (start / videoSize) * videoDuration + currentTrackAt;

  res.on('close', () => {
    saveCurrentTime(fileId, elapsedTime);
  });

  res.on('finish', () => {
    saveCurrentTime(fileId, elapsedTime);
  });
};

const saveCurrentTime = async (fileId, currentTime) => {
  const fileRepository = AppDataSource.getRepository(FileModel);
  const videoFile = await fileRepository.findOne({ where: { id: fileId } });

  if (videoFile) {
    videoFile.currentTrackAt = currentTime; 
    await fileRepository.save(videoFile);
  }
};


// ? Export the fileController
export { fileController };