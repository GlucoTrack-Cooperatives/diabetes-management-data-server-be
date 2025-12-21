from http import HTTPStatus

from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uuid
from fastapi import Depends
import logging

from config.database import get_db
from dao.model.Patient import Patient
from service.DexcomService import authenticate
from service.SchedulerService import SchedulerService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

scheduler_service = SchedulerService()

@app.on_event("startup")
async def startup_event():
    scheduler_service.start()

@app.on_event("shutdown")
async def shutdown_event():
    scheduler_service.shutdown()


class AuthRequest(BaseModel):
    user_uuid: uuid.UUID
    dexcom_email: str
    dexcom_password: str

@app.post("/auth")
async def auth(request: AuthRequest, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == request.user_uuid).first()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    if patient.dexcom_email and patient.dexcom_password:
        raise HTTPException(status_code=400, detail="Patient already has Dexcom credentials")

    auth_success = authenticate(request.dexcom_email, request.dexcom_password)

    if auth_success:
        patient.dexcom_email = request.dexcom_email
        patient.dexcom_password = request.dexcom_password
        db.commit()
        db.refresh(patient)
    else:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    return HTTPStatus.OK

