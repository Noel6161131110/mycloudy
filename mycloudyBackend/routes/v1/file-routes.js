import express from "express";
import { fileController } from '../../controllers/file-controller.js';
import multer from "multer";
import path from "path";

// Setup disk storage for uploaded files
const storage = multer.diskStorage({
    destination: function (req, file, cb) {
      cb(null, 'storage/'); // Directory to save the uploaded files
    },
    filename: function (req, file, cb) {
      const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
      cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
    }
});
  
// Set Multer middleware
const upload = multer({
storage: storage,
limits: { fileSize: 1 * 1024 * 1024 * 1024 }, // Max file size: 1GB
});

const fileRouter = express.Router();

// * File Routes
fileRouter.post("/upload-file", upload.single('file') ,fileController.UploadFile)
fileRouter.get("/get-files", fileController.GetFiles)

// * Vidoe Route
fileRouter.get("/stream-video", fileController.StreamVideo)
fileRouter.get("/get-info/video", fileController.GetVideoInfo)
fileRouter.post("/save-video-time", fileController.SaveCurrentTime)

// * Image Route
fileRouter.get("/show-image", fileController.ShowImage)

// * Audio Route
fileRouter.get("/stream-audio", fileController.StreamAudio)

export { fileRouter };