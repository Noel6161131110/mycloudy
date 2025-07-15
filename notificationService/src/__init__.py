from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from uuid import uuid4
# from src.app.v1.routes import router as v1Router
import os, sys, uvicorn, asyncio
from dotenv import load_dotenv

load_dotenv()

sys.dont_write_bytecode = True

IS_PRODUCTION = os.getenv("ENV_MODE") == "PRODUCTION"


@asynccontextmanager
async def lifespan(app : FastAPI):
    yield


app = FastAPI(
    lifespan=lifespan,
    title="MyCloudy Notification Service",
    version="v1",
    description="Auth and User Management Service for MyCloudy Self-hosted Server",
    docs_url=None if IS_PRODUCTION else "/docs",
    redoc_url=None if IS_PRODUCTION else "/redoc",  
    )

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# app.include_router(v1Router, prefix="/api/v1")


async def main():

    config = uvicorn.Config(app, host='0.0.0.0')
    server = uvicorn.Server(config)

    # Run the server
    await server.serve()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped by user.")