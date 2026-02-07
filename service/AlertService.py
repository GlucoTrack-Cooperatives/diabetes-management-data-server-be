import logging
from datetime import datetime
from uuid import UUID
from zoneinfo import ZoneInfo

from config.database import SessionLocal
from dao.model.Alert import Alert

logger = logging.getLogger(__name__)

# Europe/Warsaw timezone
WARSAW_TZ = ZoneInfo("Europe/Warsaw")


class AlertService:
    def __init__(self):
        logger.info(f"✓ Alert Service initialized - Using database for alerts")

    def check_and_send_alert(self, patient_id: UUID, glucose_value: int, timestamp: datetime,
                             low_threshold: int = 70, high_threshold: int = 200):
        alert_type = None
        severity = None

        if glucose_value < low_threshold:
            alert_type = "LOW"
            severity = "CRITICAL"
        elif glucose_value > high_threshold:
            alert_type = "HIGH"
            severity = "WARNING"

        if alert_type:
            # Ensure timestamp has timezone (convert to Warsaw if naive)
            if timestamp.tzinfo is None:
                timestamp_tz = timestamp.replace(tzinfo=WARSAW_TZ)
            else:
                timestamp_tz = timestamp.astimezone(WARSAW_TZ)

            # Current time in Warsaw timezone
            created_at_tz = datetime.now(WARSAW_TZ)

            # Create descriptive message
            if alert_type == "LOW":
                message = f"CRITICAL: Low glucose alert - {glucose_value} mg/dL detected (below {low_threshold} mg/dL)"
            else:  # HIGH
                message = f"WARNING: High glucose alert - {glucose_value} mg/dL detected (above {high_threshold} mg/dL)"

            success = self._save_alert_to_database(
                patient_id=patient_id,
                timestamp=timestamp_tz,
                severity=severity,
                message=message
            )
            logger.warning(f"🚨 {severity} {alert_type} alert for patient {patient_id}: {glucose_value} mg/dL")
            return success

        return False

    def _save_alert_to_database(self, patient_id: UUID, timestamp: datetime, severity: str, message: str):
        """Save alert directly to database"""
        db = SessionLocal()
        try:
            alert = Alert(
                patient_id=patient_id,
                timestamp=timestamp,
                severity=severity,
                message=message,
                is_acknowledged=False,
                created_at=datetime.now(WARSAW_TZ)
            )

            db.add(alert)
            db.commit()
            db.refresh(alert)

            logger.info(f"✓ Alert saved to database: ID={alert.id}, Patient={patient_id}")
            return True

        except Exception as e:
            logger.error(f"✗ Failed to save alert to database: {e}", exc_info=True)
            db.rollback()
            return False
        finally:
            db.close()

_alert_service = None


def get_alert_service() -> AlertService:
    global _alert_service
    if _alert_service is None:
        _alert_service = AlertService()
    return _alert_service
