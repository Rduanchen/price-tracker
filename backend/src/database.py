from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.config import DATABASE_URL  # FIXME


Base = declarative_base()
db_engine = create_engine("sqlite:///news_database.db", echo=True)
Base.metadata.create_all(db_engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)


def open_database_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
