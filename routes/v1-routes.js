import express from 'express';
import { fileRouter } from './v1/file-routes.js';

// * Create a router for version 1 APIs
const v1Router = express.Router();

// * Middleware to forward the request to the appropriate routers.
v1Router.use('/file-service', fileRouter);


// ? Export the v1Router
export { v1Router };