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
    type: otp.OTPType,
    recipient_id,
    email: EmailStr,
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.id == recipient_id).first()

    if user is not None:
        if user.is_verified:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"You are already verified, You can try logging in")

    pre_otp = db.query(models.OtpModel).filter(
        models.OtpModel.recipient_id == recipient_id).first()

    if pre_otp is not None:
        db.delete(pre_otp)
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
        print("Integrate with SMS")
    else:
        print("Send via email")

    try:

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
        db.delete(pre_otp)
        db.commit()

    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"User not found")
    else:
        if user.is_verified:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"You are already verified, You can try logging in")
        otp_code = otp.random(6)
        otp_object = models.OtpModel(otp_code=otp_code,
                                     recipient_id=recipient_id,
                                     created_on=datetime.now(),
                                     expiry_time=datetime.now() + timedelta(minutes=5))
        db.add(otp_object)
        db.commit()
        db.refresh(otp_object)

        if type == 'Phone':
            print("Integrate with SMS")
        else:
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

    if user.is_verified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="You are already verified!")

    if otp_blocks.expiry_time < datetime.now() or otp_blocks.is_expired:
        otp_blocks.is_expired = True
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="This otp code has already expired, Please request a new one!")

    else:

        if request.otp_code != otp_blocks.otp_code:
            otp_blocks.otp_failed_count += 1

            if otp_blocks.otp_failed_count > 5:
                otp_blocks.otp_failed_time = datetime.now() + timedelta(minutes=5)
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="You tried too many times, you've been banned for 5 mins")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Incorrect OTP, Please Try Again!")

        else:

            user.is_verified = True
            db.commit()
            db.refresh(user)

            try:
                db.delete(otp_blocks)
                db.commit()
            except:
                print(
                    f"Error occured while deleting otp model db")

            return "Otp Verified Successfully!"
