from ast import Delete
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import models
import database
import schemas
from .oauth2 import get_current_user
import uuid
from psycopg2 import connect

router = APIRouter(
    prefix='/friend/request',
    tags=["Friend Request"]
)
get_db = database.get_db


class SendRequest(schemas.BaseModel):
    to_user_id: str


class ShowRequest(schemas.BaseModel):
    id: str


class DeleteFriend(schemas.BaseModel):
    friend_id: str


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

        # conn = connect('dbname=user_fastapi')
        # cur = conn.cursor()
        # stmt = 'UPDATE user SET example_value=%s'
        # a = receiver.friends.append(str(sender_id))
        # b = sender.friends.append(str(user["user_id"]))
        # new_values = [a, b]
        # cur.execute(stmt, (new_values,))

        # conn.commit()
        # if receiver.friends == []:
        #     receiver.friends = []
        # else:
        #     receiver.friends = [str(receiver.friends)]

        # if sender.friends == []:
        #     sender.friends = []
        # else:
        #     sender.friends = [str(sender.friends)]

        mylist = list(receiver.friends)
        mylist.append(str(sender_id))

        receiver.friends = mylist

        mylist2 = list(sender.friends)
        mylist2.append(str(user["user_id"]))

        sender.friends = mylist2

        db.commit()

        print(receiver.friends)
        print(sender.friends)

        db.delete(friend_request)
        db.commit()

        return "Friend Request Accepted!"
    else:
        raise HTTPException(
            status_code=404, detail="Friend Request not Accepted!")


@router.delete('/delete', status_code=200)
async def delete_friend(request: DeleteFriend,
                        db: Session = Depends(get_db),
                        user: schemas.User = Depends(get_current_user)):

    userCheck = db.query(models.User).filter(
        models.User.id == user["user_id"]).first()

    if userCheck is None:
        raise HTTPException(status_code=400, detail=f"User Not Found!")
    elif request.friend_id is None or request.friend_id == "":
        raise HTTPException(
            status_code=400, detail="Field cant be left Blank!")

    friendCheck = db.query(models.User).filter(
        models.User.id == request.friend_id).first()

    if friendCheck is None:
        raise HTTPException(status_code=400, detail="User Not Found!")

    friends_list = list(userCheck.friends)
    length = len(friends_list)
    count = 0
    for i in range(length):
        a = friends_list[i]
        if a == request.friend_id:
            count = 1
            friends_list.pop(a)
    if count == 0:
        raise HTTPException(
            status_code=400, detail="You are not friends with this user!")

    userCheck.friends = friends_list

    db.commit()

    return "Friend Removed Successfully !"
