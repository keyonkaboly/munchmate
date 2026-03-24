from app.infrastructure.database.database import engine, Base
from app.infrastructure.database import models

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
