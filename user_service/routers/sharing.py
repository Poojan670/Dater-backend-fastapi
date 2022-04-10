from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
import database
import schemas
import models
from sqlalchemy.orm import Session
from .oauth2 import get_current_user

router = APIRouter(
    prefix="/share",
    tags=["Sharing Profiles!"]
)


@router.post("/", status_code=200, description="Share your user profile to others!")
async def share_user_profile(db: Session = Depends(database.get_db),
                             user: schemas.User = Depends(get_current_user)):

    userCheck = db.query(models.User).filter(
        models.User.id == user['user_id']).first()
    if userCheck is None:
        raise HTTPException(status_code=400, detail="User Not Found!")

    userProfile = db.query(models.UserDetails).filter(
        models.UserDetails.user_id == user["user_id"]).first()
    if userProfile is None:
        raise HTTPException(status_code=400, detail="User Details Not Found!")

    userImage = db.query(models.ImagesModel).filter(
        models.ImagesModel.user_id == user["user_id"]).first()
    if userImage is None:
        raise HTTPException(status_code=400, detail="User Image Not Found!")

    return {
        "detail": "Successfully Shared!",
        "profile_id": userProfile.id,
        "name": "{} ""{}"" {}".format(userProfile.first_name, userProfile.middle_name, userProfile.last_name),
        "image": userImage.image_url
    }
