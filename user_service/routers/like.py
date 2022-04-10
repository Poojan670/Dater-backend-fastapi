from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import database
import schemas
import models
from pydantic import BaseModel
from .oauth2 import get_current_user
import uuid

router = APIRouter(
    prefix='/likes',
    tags=['Like User']
)


class Like(BaseModel):
    like: bool
    like_to: str


@router.post('/', status_code=200)
async def like_user(request: Like,
              db: Session = Depends(database.get_db),
              user: schemas.User = Depends(get_current_user)):

    like_to = db.query(models.User).filter(
        models.User.id == request.like_to).first()

    like_check = db.query(models.LikeModel).filter_by(
        liked_by_id=user['user_id'],
        liked_to_id=request.like_to
    ).first()

    if like_to is None:
        raise HTTPException(status_code=400, detail="User Not Found!")

    elif request.like == False:
        raise HTTPException(status_code=400)

    elif like_check is not None:
        raise HTTPException(
            status_code=400, detail=f"User Already Liked!")

    like_user = models.LikeModel(
        id=uuid.uuid4(),
        like=request.like,
        liked_by_id=user['user_id'],
        liked_to_id=request.like_to
    )

    like_to.likes_count += 1
    like_to.liked_by.append(user['user_id'])
    db.commit()

    db.add(like_user)
    db.commit()
    db.refresh(like_user)

    return "Liked Successfully!"

