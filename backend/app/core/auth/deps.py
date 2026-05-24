from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from jose import jwt, JWTError

from app.core.config import settings

security = HTTPBearer()
ALGORITHM = "HS256"


def get_current_user(token=Depends(security)):
    try:
        payload = jwt.decode(
            token.credentials,
            settings.JWT_SECRET,
            algorithms=[ALGORITHM]
        )
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        return int(user_id)

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
