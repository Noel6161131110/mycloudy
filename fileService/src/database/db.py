from sqlmodel import SQLModel
import os
from dotenv import load_dotenv
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

load_dotenv()

# Define the database URL for PostgreSQL
DATABASE_URL = (
    f"postgresql+asyncpg://{os.getenv('DB_USER')}:"
    f"{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:"
    f"{os.getenv('DB_PORT')}/"
    f"{os.getenv('DATABASE')}"
)

# Create the engine for PostgreSQL
engine = create_async_engine(DATABASE_URL, echo=True)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

def getSession():
    return async_session()

async def initDB():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)