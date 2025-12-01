from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    try:
        with open("c:/Users/badda/Desktop/MastersProject/backend/startup.log", "a") as f:
            f.write("DB: get_db called\n")
    except:
        pass
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
