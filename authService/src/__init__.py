from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.database.db import initDB, getSession
from src.database.redis import getRedis, closeRedis
from src.app.v1.Users.models.models import Roles
from sqlmodel import select
from uuid import uuid4
from src.app.v1.routes import router as v1Router
import os, sys, uvicorn, asyncio
from dotenv import load_dotenv

load_dotenv()

sys.dont_write_bytecode = True

IS_PRODUCTION = os.getenv("ENV_MODE") == "PRODUCTION"

async def ensureDefaultRoles():
    async with getSession() as session:
        for roleName in ["admin", "member"]:
            stmt = select(Roles).where(Roles.name == roleName, Roles.createdBy == None)
            result = await session.exec(stmt)
            existingRole = result.first()
            if not existingRole:
                newRole = Roles(id=uuid4(), name=roleName, createdBy=None)
                session.add(newRole)
        await session.commit()
        

@asynccontextmanager
async def lifespan(app : FastAPI):
    await initDB()
    await ensureDefaultRoles()
    await getRedis()
    yield
    await closeRedis()


app = FastAPI(
    lifespan=lifespan,
    title="MyCloudy Auth and User Service",
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

app.include_router(v1Router, prefix="/v1")


        
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