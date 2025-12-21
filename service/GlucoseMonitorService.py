import logging
from datetime import datetime
from sqlalchemy.orm import Session

import random

from config.database import SessionLocal
from dao.model.Patient import Patient
from dao.model.GlucoseReading import GlucoseReading
from service.DexcomService import get_current_glucose
from service.AlertService import get_alert_service

logger = logging.getLogger(__name__)

try:
    logger.info("🔄 Initializing Alert Service...")
    alert_service = get_alert_service()
    logger.info("✅ Alert Service initialized successfully!")
except Exception as e:
    logger.error(f"❌ Failed to initialize Alert Service: {e}", exc_info=True)
    alert_service = None

def fetch_glucose_readings_for_all_users():
    db: Session = SessionLocal()
    try:
        logger.info("Starting glucose reading fetch job...")

        patients = db.query(Patient).filter(
            Patient.dexcom_email.isnot(None),
            Patient.dexcom_email != '',
            Patient.dexcom_password.isnot(None),
            Patient.dexcom_password != ''
        ).all()

        logger.info(f"Found {len(patients)} patients with Dexcom credentials")

        readings_saved = 0
        for patient in patients:
            try:
                reading_data = get_current_glucose(patient)

                if reading_data is None:
                    logger.warning(f"No reading available for patient {patient.id}, using random data")
                    reading = GlucoseReading(
                        patient_id=patient.id,
                        timestamp=datetime.utcnow(),
                        value=random.randint(10, 250),
                        trend="FLAT",
                        source="mock"
                    )
                else:
                    reading = GlucoseReading(
                        patient_id=patient.id,
                        timestamp=datetime.strptime(reading_data['timestamp'], "%Y-%m-%d %H:%M:%S"),
                        value=reading_data['value'],
                        trend=reading_data['trend'],
                        source="dexcom"
                    )

                db.add(reading)
                db.commit()
                readings_saved += 1

                logger.info(f"Saved reading for patient {patient.id}: {reading.value} mg/dL (source: {reading.source})")

                # Check for alerts
                if alert_service is not None:
                    try:
                        alert_service.check_and_send_alert(
                            patient_id=patient.id,
                            glucose_value=reading.value,
                            timestamp=reading.timestamp
                        )
                    except Exception as alert_error:
                        logger.error(f"❌ ALERT SERVICE ERROR: {alert_error}", exc_info=True)
                else:
                    logger.warning("⚠️ Alert service is None - skipping alert check")

            except Exception as e:
                logger.error(f"Error fetching reading for patient {patient.id}: {e}")
                db.rollback()
                continue

        logger.info(f"Glucose reading fetch job completed. Saved {readings_saved} readings.")

    except Exception as e:
        logger.error(f"Error in glucose reading fetch job: {e}")
    finally:
        db.close()