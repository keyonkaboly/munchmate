from fastapi import Depends, HTTPException, status
from app.infrastructure.security.auth import get_current_user

def required_role(required_role: str):
   
    def dependency(user: dict = Depends(get_current_user)):
        if user.get("role") != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"{required_role.capitalize()} access required"
            )
        return user
    return dependency