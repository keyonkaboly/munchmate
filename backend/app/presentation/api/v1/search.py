"""Module for global search bar endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.infrastructure.database.database import get_db
from app.infrastructure.database.models import Restaurant


router = APIRouter(prefix="/search", tags=["search"])


@router.get("/restaurants")
def search_restaurants(query: str, db: Session = Depends(get_db)):
    """Search restaurants by name or category."""
    if not query or not query.replace(" ", "").isalnum():
        raise HTTPException(
            status_code=400,
            detail="Search query must contain only alphanumeric characters and spaces"
        )

    results = db.query(Restaurant).filter(
        Restaurant.name.ilike(f"%{query}%") |
        Restaurant.category.ilike(f"%{query}%")
    ).all()

    if not results:
        return {"results": [], "message": "No restaurants found"}

    return {
        "results": [
            {"restaurant_id": r.id, "name": r.name, "category": r.category}
            for r in results
        ]
    }