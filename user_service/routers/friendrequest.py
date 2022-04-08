from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import models
import database
import schemas
from .oauth2 import get_current_user
import uuid

router = APIRouter(
    prefix='/friend/request',
    tags=["Friend Request"]
)
get_db = database.get_db


class SendRequest(schemas.BaseModel):
    to_user_id: str


class ShowRequest(schemas.BaseModel):
    id: str


@router.post('send/', status_code=200)
async def send_friend_request(request: SendRequest,
                              db: Session = Depends(get_db),
                              user: schemas.User = Depends(get_current_user)):
    user_check = db.query(models.User).filter(
        models.User.id == request.to_user_id).first()

    request_check = db.query(models.FriendRequest).filter_by(
        from_user_id=user['user_id'],
        to_user_id=request.to_user_id
    ).first()

    if user_check is None:
        raise HTTPException(
            status_code=400, detail=f"User not Found!")

    elif request_check is not None:
        raise HTTPException(
            status_code=400, detail=f"Friend Request was already sent to this user!")

    elif user['user_id'] == request.to_user_id:
        raise HTTPException(
            status_code=400, detail=f"You can't send request to yourself!")

    elif user["user_id"] in user_check.friends:
        raise HTTPException(
            status_code=400, detail=f"You two are already friends!")

    send_request = models.FriendRequest(
        id=str(uuid.uuid4()),
        from_user_id=user['user_id'],
        to_user_id=request.to_user_id
    )

    db.add(send_request)
    db.commit()
    db.refresh(send_request)

    return {
        "friend_id": send_request.id,
        "detail": "Friend Request Sent"
    }


@router.post('accept/{id}', status_code=200)
async def accept_friend_request(id,
                                db: Session = Depends(get_db),
                                user: schemas.User = Depends(get_current_user)):

    friend_request = db.query(models.FriendRequest).filter(
        models.FriendRequest.id == id).first()

    if friend_request is None:
        raise HTTPException(status_code=400, detail=f"Request Not Found!")

    sender_id = friend_request.from_user_id

    if friend_request.to_user_id == user['user_id']:

        receiver = db.query(models.User).filter(
            models.User.id == user['user_id']).first()

        sender = db.query(models.User).filter(
            models.User.id == sender_id).first()

        if receiver.friends is not []:
            receiver.friends = []
        if sender.friends is not []:
            sender.friends = []

        receiver.friends.append(str(sender_id))

        sender.friends.append(str(user["user_id"]))

        db.commit()

        print(receiver.friends)

        db.delete(friend_request)
        db.commit()

        return "Friend Request Accepted!"
    else:
        raise HTTPException(
            status_code=404, detail="Friend Request not Accepted!")
