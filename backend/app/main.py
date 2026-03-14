from fastapi import FastAPI
from app.presentation.api.v1 import authorization
from app.presentation.api.routers.users import router
from app.infrastructure.database.database import Base, engine
from app.presentation.api.v1 import restaurants
from app.presentation.api.v1 import checkout



app = FastAPI(title="munchmate")

# Creates tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(router)

# Include restaurant router after authorization, making sure auth is checked before getting access to the restaurant endpoints
app.include_router(restaurants.router)

app.include_router(checkout.router)

# Creates endpoint
@app.get("/")
def root():
    return{"message": "Success: FastAPI is running."}