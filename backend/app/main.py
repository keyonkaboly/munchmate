from fastapi import FastAPI
from app.presentation.api.v1 import authorization
from app.presentation.api.routers.users import router_user
from app.infrastructure.database.database import Base, engine
from app.presentation.api.v1 import restaurants
<<<<<<< HEAD
from app.presentation.api.routers.authentication import router_auth


=======
from app.presentation.api.v1 import orders
>>>>>>> 1b5051a9cc418ca88cf159ca413ec61cd4e7c42f

app = FastAPI(title="munchmate")

# Creates tables
Base.metadata.create_all(bind=engine)

# Include routers
#app.include_router(authorization.router)
app.include_router(router_user)

#include authorization router
app.include_router(router_auth)

# Include restaunrant router after authorization, making sure auth is checked before getting access to the resstaurant endpoints
app.include_router(restaurants.router)   

# registers routes defined in orders.py with main FastAPI
app.include_router(orders.router)

# Creates endpoint
@app.get("/")
def root():
    return{"message": "Success: FastAPI is running."}