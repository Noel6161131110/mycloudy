import 'dotenv/config';
import fs from "fs";

const fileController = {};


// * Function to upload files
fileController.UploadFile = async (req, res) => {
  if (!req.file) {
    return res.status(400).send('No file uploaded.');
  }
  // File successfully uploaded
  return res.send({ message: 'File uploaded successfully!', fileName: req.file.filename });
}

// * Function to stream video
fileController.StreamVideo = async (req, res) => {
    const range = req.headers.range;
    if (!range) {
      return res.status(400).send("Requires Range header");
    }
  
    const videoPath = process.env.TEST_VIDEOS_PATH;
    const videoSize = fs.statSync(videoPath).size;
  
    // Parse the range header to get start and end bytes
    const CHUNK_SIZE = 10 ** 6; // 1MB per chunk
    const start = Number(range.replace(/\D/g, "")); // Extract start byte
    const end = Math.min(start + CHUNK_SIZE - 1, videoSize - 1); // Ensure end byte does not exceed video size
  
    // Create headers for the response
    const contentLength = end - start + 1;
    const headers = {
      "Content-Range": `bytes ${start}-${end}/${videoSize}`,
      "Accept-Ranges": "bytes",
      "Content-Length": contentLength,
      "Content-Type": "video/mp4",
    };
  
    // Send the response with status code 206 (Partial Content)
    res.writeHead(206, headers);
  
    // Create a read stream for the video chunk
    const videoStream = fs.createReadStream(videoPath, { start, end });
    videoStream.pipe(res);
}


// ? Export the fileController
export { fileController };