from fastapi import Header, HTTPException

from constants import TOKEN


def authenticate_token(token: str = Header(...)):
    if token != TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    return True
