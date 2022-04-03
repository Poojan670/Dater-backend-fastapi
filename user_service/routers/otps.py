import asyncio
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import EmailStr
import schemas
import database
import models
from sqlalchemy.orm import Session
from otp_check import otp
from datetime import datetime, timedelta
import nest_asyncio
from .producer import SendEmailProducer
import json
nest_asyncio.apply()

router = APIRouter(
    prefix='/otp',
    tags=['otps']
)

get_db = database.get_db


def send_otp(
    type,
    recipient_id,
    email: EmailStr,
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.id == recipient_id).first()

    pre_otp = db.query(models.OtpModel).filter(
        models.OtpModel.recipient_id == recipient_id).first()

    if pre_otp is not None:
        pre_otp.delete(synchronize_session=False)
        db.commit()

    otp_code = otp.random(6)
    otp_object = models.OtpModel(otp_code=otp_code,
                                 recipient_id=recipient_id,
                                 created_on=datetime.now(),
                                 expiry_time=datetime.now() + timedelta(minutes=5))
    db.add(otp_object)
    db.commit()
    db.refresh(otp_object)

    if type == 'Phone':
        if user is not None:
            if user.is_phone_verified:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=f"You are already verified, You can try logging in")
        print("Integrate with SMS")

        print(otp_code)

        return {
            "recipient_id": otp_object.recipient_id,
            "otp_code": otp_object.otp_code,
        }

    else:
        print("Send via email")

        try:
            if user.is_email_verified:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=f"You have already verified this email!")

            producer = SendEmailProducer()
            email_obj = {
                "type": "SendEmail",
                "email": email,
                "otp": otp_code,
                "user_id": recipient_id
            }
            producer.send_msg_async(json.dumps(email_obj))

        except RuntimeError as e:
            print(str(e))

        print(otp_code)

        return {
            "recipient_id": otp_object.recipient_id,
            "otp_code": otp_object.otp_code,
        }


@router.post('/resend')
def resend_otp(
    type: otp.OTPType,
    recipient_id,

    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.id == recipient_id).first()

    pre_otp = db.query(models.OtpModel).filter(
        models.OtpModel.recipient_id == recipient_id).first()

    if pre_otp is not None:
        pre_otp.delete(synchronize_session=False)
        db.commit()

    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"User not found")
    else:
        if type == 'Phone':

            if user.is_phone_verified:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=f"You are already phone verified, You can try logging in")
            otp_code = otp.random(6)
            otp_object = models.OtpModel(otp_code=otp_code,
                                         recipient_id=recipient_id,
                                         created_on=datetime.now(),
                                         expiry_time=datetime.now() + timedelta(minutes=5))
            db.add(otp_object)
            db.commit()

            print("Integrate with SMS")

            print(otp_code)

            return {
                "recipient_id": otp_object.recipient_id,
                "otp_code": otp_object.otp_code,
            }

        else:
            if user.is_email_verified:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=f"You are already email verified!")

            otp_code = otp.random(6)
            otp_object = models.OtpModel(otp_code=otp_code,
                                         recipient_id=recipient_id,
                                         created_on=datetime.now(),
                                         expiry_time=datetime.now() + timedelta(minutes=5))
            db.add(otp_object)
            db.commit()

            print("Send via email")

            try:
                producer = SendEmailProducer()
                email_obj = {
                    "type": "ReSendEmail",
                    "email": user.email,
                    "otp": otp_code,
                    "user_id": recipient_id
                }
                producer.send_msg_async(json.dumps(email_obj))

            except Exception as e:
                print(str(e))

            print(otp_code)

            return {
                "recipient_id": otp_object.recipient_id,
                "otp_code": otp_object.otp_code,
            }


@router.post('/verify/{id}', status_code=status.HTTP_201_CREATED)
async def verify_otp(
    id,
    request: schemas.VerifyOTP,
    db: Session = Depends(get_db)
):

    otp_blocks = db.query(models.OtpModel).filter(
        models.OtpModel.recipient_id == id).first()
    if otp_blocks is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Otp Model Object not found!")

    try:
        user = db.query(models.User).filter(
            models.User.id == id).first()
    except Exception as e:
        print(str(e))

    if user.is_phone_verified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="You are already verified!")

    try:
        if otp_blocks.otp_failed_time > datetime.now():
            time = otp_blocks.otp_failed_time - datetime.now()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"You're banned for {time} minutes")
    except TypeError:
        print("Okay!")

    if otp_blocks.expiry_time < datetime.now() or otp_blocks.is_expired:
        otp_blocks.is_expired = True
        db.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="This otp code has already expired, Please request a new one!")

    else:

        if request.otp_code != otp_blocks.otp_code:
            otp_blocks.otp_failed_count += 1
            db.commit()

            if otp_blocks.otp_failed_count >= 5:
                otp_blocks.otp_failed_time = datetime.now() + timedelta(minutes=2)
                otp_blocks.otp_failed_count = 0
                db.commit()
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="You tried too many times, you've been banned for 2 mins")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Incorrect OTP, Please Try Again!")

        else:

            user.is_phone_verified = True
            db.commit()
            db.refresh(user)

            try:
                db.delete(otp_blocks)
                db.commit()
            except:
                print(
                    f"Error occured while deleting otp model db")

            return "Otp Verified Successfully!"


@router.post('/verify/email/{id}', status_code=status.HTTP_201_CREATED)
async def verify_email(
    id,
    request: schemas.VerifyOTP,
    db: Session = Depends(get_db)
):

    otp_blocks = db.query(models.OtpModel).filter(
        models.OtpModel.recipient_id == id).first()
    if otp_blocks is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Otp Model Object not found!")

    try:
        user = db.query(models.User).filter(
            models.User.id == id).first()
    except Exception as e:
        print(str(e))

    if user.is_email_verified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="You are already verified!")

    try:
        if otp_blocks.otp_failed_time > datetime.now():
            time = otp_blocks.otp_failed_time - datetime.now()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"You're banned for {time} minutes")
    except TypeError:
        print("Okay!")

    if otp_blocks.expiry_time < datetime.now() or otp_blocks.is_expired:
        otp_blocks.is_expired = True
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="This otp code has already expired, Please request a new one!")

    else:

        if request.otp_code != otp_blocks.otp_code:
            otp_blocks.otp_failed_count += 1
            db.commit()

            if otp_blocks.otp_failed_count >= 5:
                otp_blocks.otp_failed_time = datetime.now() + timedelta(minutes=2)
                otp_blocks.otp_failed_count = 0
                db.commit()
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="You tried too many times, you've been banned for 2 mins")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Incorrect OTP, Please Try Again!")

        else:

            user.is_email_verified = True
            db.commit()
            db.refresh(user)

            await asyncio.sleep(0.25)

            try:
                producer = SendEmailProducer()
                email_obj = {
                    "type": "VerifiedEmail",
                    "email": user.email,
                }
                producer.send_msg_async(json.dumps(email_obj))

            except Exception as e:
                print(str(e))

            await asyncio.sleep(0.25)

            try:
                db.delete(otp_blocks)
                db.commit()
            except:
                print(
                    f"Error occured while deleting otp model db")

            return "Otp Verified Successfully!"
