from fastapi import FastAPI
from app.presentation.api.v1 import authorization
from app.infrastructure.db.database import Base, engine

app = FastAPI(title="munchmate")

# Creates tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(authorization.router)

# Creates endpoint
@app.get("/")
def root():
    return{"message": "Success: FastAPI is running."}