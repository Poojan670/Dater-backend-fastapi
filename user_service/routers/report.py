from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import database
import models
import schemas
from .oauth2 import get_current_user
import uuid
from roles import *
import asyncio

router = APIRouter(
    prefix='/report',
    tags=['Report User']
)


@router.post('/', status_code=200)
async def report_user(request: schemas.ReportBase,
                      db: Session = Depends(database.get_db),
                      user: schemas.User = Depends(get_current_user)):

    userCheck = db.query(models.User).filter(
        models.User.id == request.report_to_id).first()
    if request.report_to_id == user['user_id']:
        raise HTTPException(
            status_code=400, detail=f"You can't report yourself!")
    elif userCheck is None:
        raise HTTPException(status_code=400, detail=f"User not Found!")
    report = models.ReportUser(uuid.uuid4(),
                               report_by_id=user['user_id'],
                               report_to_id=request.report_to_id,
                               report_reason=request.report_reason
                               )
    if userCheck.report_count > 20:
        userCheck.is_suspended = True
        userCheck.suspended_count += 1
        userCheck.suspend_timestamp = datetime.now() + timedelta(days=2)
        db.commit()
    else:
        userCheck.report_count += 1
        db.commit()

    await asyncio.sleep(0.25)

    db.add(report)
    db.commit()
    db.refresh(report)

    return {
        "report_to_id": report.report_to_id,
        "report_reason": report.report_reason,
        "detail": "User Successfully Reported!"
    }


@router.get('/all', status_code=200, response_model=schemas.ReportList)
async def list_all_reports(db: Session = Depends(database.get_db),
                           admin=Depends(allow_create_resource)):
    objects = db.query(models.ReportUser).all()
    await asyncio.sleep(0.5)
    return objects
