from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.database.db import initDB
from src.app.v1.routes import router as v1Router
import os, sys, uvicorn, asyncio
from dotenv import load_dotenv
from datetime import datetime
from uuid import uuid4
from sqlmodel import Session, select
from src.app.v1.Folders.models.models import Folders, Tags
from src.database.db import engine
load_dotenv()

VAULT_DIR = "MYCLOUDY_VAULT"

sys.dont_write_bytecode = True

IS_PRODUCTION = os.getenv("ENV_MODE") == "PRODUCTION"


def initializeVaultAndDefaults():
    if not os.path.exists(VAULT_DIR):
        os.makedirs(VAULT_DIR, exist_ok=True)
        # os.chmod(VAULT_DIR, 0o700)  # Uncomment if you want strict FS permissions

    with Session(engine) as session:
        # Ensure root folder record exists
        existing_folder = session.exec(select(Folders).where(Folders.name == VAULT_DIR)).first()
        if not existing_folder:
            root_folder = Folders(
                id=uuid4(),
                name=VAULT_DIR,
                createdBy=None,
                parentId=None,
                createdAt=datetime.now(),
                updatedAt=datetime.now(),
                isSystem=True,
                description="Root folder for MyCloudy Vault"
            )
            session.add(root_folder)
            session.commit()

        # Create default tags if they don't exist
        defaultTags = ["Movies", "Music", "Photos", "Documents"]
        for tagName in defaultTags:
            tag = session.exec(select(Tags).where(Tags.name == tagName)).first()
            if not tag:
                tag = Tags(
                    id=uuid4(),
                    name=tagName,
                    createdBy=None,
                    createdAt=datetime.now()
                )
                session.add(tag)
                session.commit()
                
                
@asynccontextmanager
async def lifespan(app : FastAPI):
    initDB()
    initializeVaultAndDefaults()

    yield


app = FastAPI(
    lifespan=lifespan,
    title="MyCloudy File Service",
    version="v1",
    description="File Service for MyCloudy Server",
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

app.include_router(v1Router, prefix="/api/v1")

async def main():
    """
    Main entry point to run the Uvicorn server.
    """
    config = uvicorn.Config(app, host='0.0.0.0')
    server = uvicorn.Server(config)

    # Run the server
    await server.serve()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped by user.")