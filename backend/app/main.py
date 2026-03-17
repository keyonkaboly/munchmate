from fastapi import FastAPI
from app.presentation.api.v1 import authorization
from app.presentation.api.routers.users import router
from app.infrastructure.database.database import Base, engine
from app.presentation.api.v1 import restaurants
from app.presentation.api.v1 import checkout
from app.presentation.api.v1 import orders
from app.presentation.api.v1 import payments
from app.presentation.api.v1 import notifications
from app.presentation.api.v1.order_router import router_order

app = FastAPI(title="munchmate")

# Creates tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(router)

# Include restaurant router after authorization, making sure auth is checked before getting access to the restaurant endpoints
app.include_router(restaurants.router)

app.include_router(checkout.router)

# registers routes defined in orders.py with main FastAPI
app.include_router(orders.router)

# registers routes defined in payments.py with main FastAPI
app.include_router(payments.router)

# registers routes defined in notifications.py with main FastAPI
app.include_router(notifications.router)

#create an order:
app.include_router(router_order)



# Creates endpoint
@app.get("/")
def root():
    return{"message": "Success: FastAPI is running."}