from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from tech.infra.settings.settings import Settings
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///:memory:"  # Default for testing

    class Config:
        env_file = ".env"



load_dotenv()
engine = create_engine(Settings().DATABASE_URL)


def get_session():  # pragma: no cover
    with Session(engine) as session:
        yield session
