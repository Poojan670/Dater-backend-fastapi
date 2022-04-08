from fastapi import APIRouter, status, Depends, HTTPException
import database
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
import models
from hashing import Hash
from .otps import forgot_password
from datetime import datetime, timedelta
import asyncio
import json
from .producer import SendEmailProducer


class PhonePasswordBase(BaseModel):
    phone: str


class PhonePassword(PhonePasswordBase):

    class Config():
        orm_mode = True


class PhoneVerifyPassword(BaseModel):
    otp_code: str
    password: str

    class Config():
        orm_mode = True


class EmailPasswordBase(BaseModel):
    email: EmailStr


class EmailPassowrd(EmailPasswordBase):
    class Config():
        orm_mode = True


class EmailVerifyPassword(BaseModel):
    otp_code: str
    password: str

    class Config():
        orm_mode = True


router = APIRouter(
    prefix='/password',
    tags=['password']
)

get_db = database.get_db


@router.post('/forgot/phone', status_code=status.HTTP_200_OK)
async def forgot_password_phone(request: PhonePassword, db: Session = Depends(get_db)):

    object = db.query(models.User).filter(models.User.phone == request.phone)
    if not object.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with this phone number not found!")

    user = object.first()

    await asyncio.sleep(0.25)

    try:
        forgot_password(type="Phone", recipient_id=user.id,
                        db=db, email=user.email)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error occured due to {e}")

    return "Otp Code has been sent to your phone, Please use it for verification!"


@router.post('/reset/phone/{id}', status_code=status.HTTP_200_OK)
async def reset_password_phone(id,
                               request: PhoneVerifyPassword,
                               db: Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.id == id).first()
    otp = db.query(models.OtpModel).filter(
        models.OtpModel.recipient_id == id).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"User Not Found!")

    elif request.password == "" or request.password is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Password can't be left blank!")

    elif otp is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Otp Model not Found!")

    try:
        if otp.otp_failed_time > datetime.now():
            time = otp.otp_failed_time - datetime.now()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"You're banned for {time} minutes")
    except TypeError:
        print("Okay!")

    await asyncio.sleep(0.25)

    if otp.expiry_time < datetime.now() or otp.is_expired:
        otp.is_expired = True
        db.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="This otp code has already expired, Please request a new one!")

    else:

        if request.otp_code != otp.otp_code:
            otp.otp_failed_count += 1
            db.commit()

            if otp.otp_failed_count >= 5:
                otp.otp_failed_time = datetime.now() + timedelta(minutes=2)
                otp.otp_failed_count = 0
                db.commit()
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="You tried too many times, you've been banned for 2 mins")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Incorrect OTP, Please Try Again!")

        user.password = Hash.bcrypt(request.password)
        db.commit()
        db.refresh(user)
        try:
            db.delete(otp)
            db.commit()
        except:
            print(
                f"Error occured while deleting otp model db")

        return "Password Changed Successfully!"


@router.post('/forgot/email', status_code=status.HTTP_200_OK)
async def forgot_password_email(request: EmailPassowrd,
                                db: Session = Depends(get_db)):

    object = db.query(models.User).filter(models.User.email == request.email)
    if not object.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with this email not found!")

    user = object.first()

    await asyncio.sleep(0.25)

    try:
        forgot_password(type="Email",
                        recipient_id=user.id,
                        db=db,
                        email=user.email)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error occured due to {e}")

    return "Otp Code has been sent to your phone, Please use it for verification!"


@router.post('/reset/email/{id}', status_code=status.HTTP_200_OK)
async def reset_password_phone(id,
                               request: EmailVerifyPassword,
                               db: Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.id == id).first()
    otp = db.query(models.OtpModel).filter(
        models.OtpModel.recipient_id == id).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"User Not Found!")

    elif request.password == "" or request.password is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Password can't be left blank!")

    elif otp is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Otp Model not Found!")

    try:
        if otp.otp_failed_time > datetime.now():
            time = otp.otp_failed_time - datetime.now()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"You're banned for {time} minutes")
    except TypeError:
        print("Okay!")

    await asyncio.sleep(0.25)

    if otp.expiry_time < datetime.now() or otp.is_expired:
        otp.is_expired = True
        db.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="This otp code has already expired, Please request a new one!")

    else:

        if request.otp_code != otp.otp_code:
            otp.otp_failed_count += 1
            db.commit()

            if otp.otp_failed_count >= 5:
                otp.otp_failed_time = datetime.now() + timedelta(minutes=2)
                otp.otp_failed_count = 0
                db.commit()
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="You tried too many times, you've been banned for 2 mins")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Incorrect OTP, Please Try Again!")

        user.password = Hash.bcrypt(request.password)
        db.commit()
        db.refresh(user)

        try:
            producer = SendEmailProducer()
            email_obj = {
                "type": "VerifiedEmailPasswordReset",
                "email": user.email,
            }
            producer.send_msg_async(json.dumps(email_obj))

        except Exception as e:
            print(str(e))

        try:
            db.delete(otp)
            db.commit()
        except:
            print(
                f"Error occured while deleting otp model db")

        return "Password Changed Successfully!"
