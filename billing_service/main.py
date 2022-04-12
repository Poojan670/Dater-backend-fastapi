from fastapi import FastAPI, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from database import get_db, engine, SessionLocal
import models
from typing import List
from enum import Enum
import jwt
import requests as req
import os

app = FastAPI()

models.Base.metadata.create_all(engine)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


@app.on_event("startup")
async def startup_event():
    with SessionLocal() as db:
        obj = db.query(models.BillingModel.id == '1').first()
        if obj is None:
            try:
                id = ['1', '2', '3']
                subscription_time_months = [3, 6, 1]
                price = [14, 10, 20]
                for i in range(3):
                    billing = models.BillingModel(
                        id=id[i],
                        subscription_time_months=subscription_time_months[i],
                        price=price[i])
                    db.add(billing)
                    db.commit()
                    db.refresh(billing)
                print("Billing Models Created Successfully!")
            except Exception as e:
                print(str(e))
        else:
            print("Okay!")


class BillingType(str, Enum):
    PlanA = "PlanA"
    PlanB = "PlanB"
    PlanC = "PlanC"


@app.post('/epay/main', status_code=200)
async def esewa_payment(request_id, amount):
    url = "https://uat.esewa.com.np/epay/main"
    d = {'amt': 100,
         'pdc': 0,
         'psc': 0,
         'txAmt': 0,
         'tAmt': 100,
         'pid': 'ee2c3ca1-696b-4cc5-a6be-2c40d929d453',
         'scd': 'EPAYTEST',
         'su': 'http://merchant.com.np/page/esewa_payment_success?q=su',
         'fu': 'http://merchant.com.np/page/esewa_payment_failed?q=fu'}
    resp = req.post(url, d)


@app.post('/billing', status_code=200, description="User Billing!")
async def post_billing(check: Request,
                       billing_plan: BillingType,
                       db: Session = Depends(get_db)):

    try:
        token = check.headers.get('Authorization')
        if token is None or token == "":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Not Authenticated!")

        token_data = token.split(" ")
        decode = jwt.decode(
            token_data[1], SECRET_KEY, algorithms=['HS256'])
        user_id = decode['user_id']
        role = decode['role']
    except jwt.ExpiredSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e}")
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e}")

    if billing_plan == "PlanA":
        obj = models.UserModel(user_id=user_id,
                               bill="1",
                               )
    elif billing_plan == "PlanB":
        obj = models.UserModel(user_id=user_id,
                               bill="2",
                               )

    elif billing_plan == "PlanC":
        obj = models.UserModel(user_id=user_id,
                               bill="2",
                               )

    esewa_payment(user_id, obj.bill)

    db.add(obj)
    db.commit()
    db.refresh(obj)

    return "You have successfully subscribed to {billing_plan} subscription!"


@app.get('/billing/{id}', status_code=200, description="User Billing Retrieve!", response_model=models.UserRetrieve)
async def get_billing(id,
                      check: Request,
                      db: Session = Depends(get_db)):

    try:
        token = check.headers.get('Authorization')
        if token is None or token == "":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Not Authenticated!")
        token_data = token.split(" ")
        decode = jwt.decode(
            token_data[1], SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e}")
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e}")

    obj = db.query(models.UserModel.id == id).first()

    if obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not Found!!")

    return obj


@app.get('/billing/all', status_code=200, description="See All User Billings!", response_model=List[models.ShowUserId])
async def show_all_billings(check: Request,
                            db: Session = Depends(get_db)):
    try:
        token = check.headers.get('Authorization')
        if token is None or token == "":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Not Authenticated!")

        token_data = token.split(" ")
        decode = jwt.decode(
            token_data[1], SECRET_KEY, algorithms=['HS256'])
        role = decode['role']
    except jwt.ExpiredSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e}")
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e}")

    object = db.query(models.UserModel).all()

    if role == "Admin":
        return object
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Not Allowed!")


@app.get('/{id}', status_code=200, response_model=models.ShowBilling)
async def show_billings(id,
                        db: Session = Depends(get_db)):

    object = db.query(models.BillingModel).filter(
        models.BillingModel.id == id).first()
    if not object:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Billing Model with the id {id} not found")
    return object
