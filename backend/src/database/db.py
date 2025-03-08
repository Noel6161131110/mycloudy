from sqlmodel import create_engine, SQLModel, Session
import os
from dotenv import load_dotenv

load_dotenv()

# Define the database URL for PostgreSQL
DATABASE_URL = (
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:"
    f"{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:"
    f"{os.getenv('DB_PORT')}/"
    f"{os.getenv('DATABASE')}"
)

# Create the engine for PostgreSQL
engine = create_engine(os.environ.get("DATABASE_URL", DATABASE_URL))

def initDB():
    # Create the database tables
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session