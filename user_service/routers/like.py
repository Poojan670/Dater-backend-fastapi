from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import database
import schemas
import models
from pydantic import BaseModel
from .oauth2 import get_current_user

router = APIRouter(
    prefix='/like',
    tags=['Like User']
)


class Like(BaseModel):
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

    like_by = db.query(models.User).filter(
        models.User.id == user['user_id']).first()

    if like_to is None:
        raise HTTPException(status_code=400, detail="User Not Found!")

    elif like_by is None:
        raise HTTPException(status_code=400, detail="User Not Found!")

    elif like_check is not None:
        raise HTTPException(
            status_code=400, detail=f"User Already Liked!")

    like_user = models.LikeModel(
        like=True,
        liked_by_id=user['user_id'],
        liked_to_id=request.like_to
    )

    like_to.likes_count += 1

    mylist = list(like_to.liked_by)
    mylist.append(str(user['user_id']))
    like_to.liked_by = mylist

    mylikes = list(like_by.likes)
    mylikes.append(str(request.like_to))
    like_by.likes = mylikes

    db.add(like_user)
    db.commit()
    db.refresh(like_user)

    return "Liked Successfully!"


@router.delete('/{id}', status_code=200, description="Unlike User!")
async def unlike_user(id,
                      db: Session = Depends(database.get_db),
                      user: schemas.User = Depends(get_current_user)):

    object = db.query(models.LikeModel).filter(models.LikeModel.id == id)
    if not object.first():
        raise HTTPException(status_code=400, detail="Like Object Not Found!")

    liked_by_user = object.first().liked_by_id
    liked_to_user = object.first().liked_to_id

    try:
        user1 = db.query(models.User).filter(
            models.User.id == liked_by_user).first()

        user1list = list(user1.likes)
        count = len(user1list)
        for i in range(0, count - 1):
            if user1list[i] == str(liked_to_user):
                user1list.pop(str(liked_to_user))
        user1.likes = user1list

    except Exception as e:
        raise HTTPException(
            status_code=404, detail="Error occured due to {}".format(str(e)))

    try:
        user2 = db.query(models.User).filter(
            models.User.id == liked_to_user).first()

        user2.likes_count -= 1
        user2list = list(user2.liked_by)
        count = len(user2list)

        for i in range(0, count - 1):
            if user2list[i] == str(liked_by_user):
                user2list.pop(str(liked_by_user))
        user2.liked_by = user2list

    except Exception as e:
        raise HTTPException(
            status_code=400, detail="Error occured due to {}".format(str(e)))

    object.delete(synchronize_session=False)
    db.commit()
    return 'Deleted Successfully'
