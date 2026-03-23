from fastapi import FastAPI
from app.infrastructure.database.database import Base, engine
from app.presentation.api.v1.authentication import router_auth
from app.presentation.api.v1 import restaurants
from app.presentation.api.v1 import checkout
from app.presentation.api.v1 import payments
from app.presentation.api.v1 import notifications
from app.presentation.api.v1 import search
from app.presentation.api.v1.order_router import router_order

app = FastAPI(title="munchmate")

# Creates tables
Base.metadata.create_all(bind=engine)

app.include_router(router_auth)

app.include_router(search.router)

# Include restaurant router after authorization, making sure auth is checked before getting access to the restaurant endpoints
app.include_router(restaurants.router)

#create an order:
app.include_router(router_order)

app.include_router(checkout.router)

# registers routes defined in payments.py with main FastAPI
app.include_router(payments.router)

# registers routes defined in notifications.py with main FastAPI
app.include_router(notifications.router)

# Creates endpoint
@app.get("/")
def root():
    return{"message": "Success: FastAPI is running."}