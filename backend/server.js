import express from "express";
import dotenv from "dotenv";
import cors from "cors";
import morgan from "morgan";
import { v1Router } from "./routes/v1-routes.js";
dotenv.config();

const app = express();

app.use(cors());
app.use(morgan('combined'));
app.use(express.json());

// * Middleware to forward the request to the v1Router
app.use('/api/v1', v1Router);

const PORT = process.env.PORT;
app.listen(PORT, function () {
  console.log("Server is running on Port: " + PORT);
});