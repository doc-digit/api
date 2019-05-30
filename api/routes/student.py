from typing import List

from fastapi import APIRouter, Query, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.models import Student
from api.utils.get_db import get_db

router = APIRouter()


class StudentOut(BaseModel):
    id: int
    name: str
    surname: str
    album_id: int
    semester: int
    course_name: str
    faculty: str


def find_student_by_name(db_session: Session, query: str):
    students = (
        db_session.query(Student).filter(Student.name.like("%" + query + "%")).all()
    )
    return students


@router.get("/find", response_model=List[StudentOut])
def find_student(q: str = Query(None, min_length=3), db: Session = Depends(get_db)):
    """
    Find student by name (currently)
    """
    students = find_student_by_name(db, q)
    return students
