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
    let Filetype;
    // Check if the file is a video by its extension
    const videoExtensions = ['mp4', 'mov', 'avi', 'mkv', 'webm'];
    const audioExtensions = ['mp3', 'wav', 'ogg', 'flac'];
    const imageExtensions = ['jpg', 'jpeg', 'png'];

    if (videoExtensions.includes(fileExtension.toLowerCase())) {
      // Use ffmpeg to get the video duration
      totalLength = await getVideoDuration(fullFilePath);
      console.log('Video duration:', totalLength);
      Filetype = 'video';
    }
    else if (audioExtensions.includes(fileExtension.toLowerCase())) {
      Filetype = 'audio';
    }
    else if (imageExtensions.includes(fileExtension.toLowerCase())) {
      Filetype = 'images';
    }
    else {
      return res.status(400).send('Invalid file type');
    }

    // Use the repository pattern to create and save the file details
    const fileRepository = AppDataSource.getRepository('FileModel'); // Ensure 'FileModel' matches your entity
    const fileDetails = fileRepository.create({
      filename,
      fileExtension,
      filePath: fullFilePath,
      fileType: Filetype,
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

// * Function to get files
fileController.GetFiles = async (req, res) => {
  const FileType = req.query.type;

  if (!FileType) {
    return res.status(400).send("Missing file type query parameter");
  }

  if (FileType !== 'video' && FileType !== 'audio' && FileType !== 'images') {
    return res.status(400).send("Invalid file type query parameter");
  }

  const fileRepository = AppDataSource.getRepository(FileModel);


  if (FileType === 'video' || FileType === 'audio' || FileType === 'images') {
    const files = await fileRepository.find({ where: { fileType : FileType } });
    return res.send({"file_result" : files});
  }

  return res.status(500).send("An error occurred while fetching files");
};

// * Function to get the info of a video
fileController.GetVideoInfo = async (req, res) => {
  const fileId = req.query.id;
  if (!fileId) {
    return res.status(400).send("Missing video ID query parameter");
  }

  const fileRepository = AppDataSource.getRepository(FileModel);
  const videoFile = await fileRepository.findOne({ where: { id: fileId } });

  if (!videoFile) {
    return res.status(404).send("Video file not found");
  }

  return res.send({
    filename: videoFile.filename,
    totalLength: videoFile.totalLength || 'Not a video file',
    currentTrackAt: videoFile.currentTrackAt || 0,
  });
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

};

// * Function to save the current time of a video
fileController.SaveCurrentTime = async (req, res) => {
  const fileId = req.body.videoId;
  const currentTime = req.body.currentTime;

  if (!fileId || !currentTime) {
    return res.status(400).send("Missing video ID or time query parameter");
  }

  await saveCurrentTime(fileId, currentTime);
  return res.send("Current time saved successfully");
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