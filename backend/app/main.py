from fastapi import FastAPI
from app.infrastructure.database.database import Base, engine
from app.presentation.api.v1.authentication import router_auth
from app.presentation.api.v1 import restaurants
from app.presentation.api.v1 import checkout
from app.presentation.api.v1 import payments
from app.presentation.api.v1 import notifications
from app.presentation.api.v1.order_router import router_order
from app.data.dataset_seed import seed_dataset_data

app = FastAPI(title="munchmate")

Base.metadata.create_all(bind=engine)
seed_dataset_data()


app.include_router(router_auth)

app.include_router(restaurants.router)

app.include_router(router_order)

app.include_router(checkout.router)

app.include_router(payments.router)

app.include_router(notifications.router)

@app.get("/")
def root():
    return{"message": "Success: FastAPI is running."}