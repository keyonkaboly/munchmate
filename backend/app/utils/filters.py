from app.infrastructure.database.models import Restaurant
from sqlalchemy.orm import Session

# takes the db connection and two optional filters (None means not provided)
def apply_dietary_filters(db: Session, is_halal: bool = None, is_vegetarian: bool = None, cuisine_type=None, return_query: bool = False):
    # command to fetch all restaurants
    query = db.query(Restaurant)
    
    if is_halal is not None:
        query = query.filter(Restaurant.is_halal == is_halal)

    if is_vegetarian is not None:
        query = query.filter(Restaurant.is_vegetarian == is_vegetarian)

    if cuisine_type:
        query = query.filter(Restaurant.cuisine_type == cuisine_type)
    
    return query if return_query else query.all()
   