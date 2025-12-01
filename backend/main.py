from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api.v1.api import api_router
from app.db import models
from app.db.base import engine

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

@app.on_event("startup")
async def startup_event():
    with open("c:/Users/badda/Desktop/MastersProject/backend/startup.log", "a") as f:
        f.write("\nSTARTUP\n")
        f.write(f"DB URL: {settings.DATABASE_URL}\n")
        f.write(f"DB Password: {settings.POSTGRES_PASSWORD}\n")
        
    # Test DB Connection
    try:
        from sqlalchemy import create_engine, text
        engine_test = create_engine(settings.DATABASE_URL)
        with engine_test.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            with open("c:/Users/badda/Desktop/MastersProject/backend/startup.log", "a") as f:
                f.write(f"DB CONNECTION TEST: SUCCESS ({result.scalar()})\n")
    except Exception as e:
        with open("c:/Users/badda/Desktop/MastersProject/backend/startup.log", "a") as f:
            f.write(f"DB CONNECTION TEST: FAILED - {str(e)}\n")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    try:
        with open("c:/Users/badda/Desktop/MastersProject/backend/global_error.log", "w") as f:
            f.write(f"Global Exception: {str(exc)}\n")
            f.write(traceback.format_exc())
    except:
        pass
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error", "details": str(exc)},
    )

app.include_router(api_router, prefix=settings.API_V1_STR)
# Main page
@app.get("/")
def root():
    return {"message": "Welcome to the Masters Project API"}
    
# Ping
@app.get("/ping")
def ping():
    with open("c:/Users/badda/Desktop/MastersProject/backend/startup.log", "a") as f:
        f.write("PING: server has been successfully pinged!\n")
    return {"message": "server has been successfully pinged"}


# Forced reload for course details endpoint
