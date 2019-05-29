from fastapi import APIRouter, Depends, Body
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.models import User
from api.exceptions import NotFoundException
from api.utils.get_db import get_db

router = APIRouter()


class UserIn(BaseModel):
    pin: int


class UserOut(BaseModel):
    id: int = None
    name: str = None


def get_user_by_pin(db_session: Session, pin: int):
    return db_session.query(User).filter(User.pin == pin).first()


@router.post("/login", response_model=UserOut, summary="Login with pin")
def login(user_in: UserIn, db: Session = Depends(get_db)):
    """
    Login with pin
    """
    user = get_user_by_pin(db, user_in.pin)
    if not user:
        raise NotFoundException

    return user
