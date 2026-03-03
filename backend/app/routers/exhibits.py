from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import crud, models, schemas, database, auth

router = APIRouter(
    prefix="/api/exhibits",
    tags=["exhibits"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=dict)
def read_exhibits(
    skip: int = 0, 
    limit: int = 10, 
    category: Optional[str] = None,
    db: Session = Depends(database.get_db)
):
    exhibits = crud.get_exhibits(db, skip=skip, limit=limit, category=category)
    total = crud.get_exhibits_count(db, category=category)
    return {"exhibits": exhibits, "total": total, "page": (skip // limit) + 1}

@router.post("/", response_model=schemas.Exhibit)
def create_exhibit(
    exhibit: schemas.ExhibitCreate, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_admin_user)
):
    return crud.create_exhibit(db=db, exhibit=exhibit)
