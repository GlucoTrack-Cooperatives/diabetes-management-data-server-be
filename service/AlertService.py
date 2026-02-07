import json
import logging
import requests
from datetime import datetime
from uuid import UUID
from zoneinfo import ZoneInfo

from google.cloud import pubsub_v1
from config.Settings import settings

logger = logging.getLogger(__name__)

# Europe/Warsaw timezone
WARSAW_TZ = ZoneInfo("Europe/Warsaw")

# Java backend internal endpoint
JAVA_ALERT_ENDPOINT = "http://glucko-java-service:8080/api/diabetes-management/internal/alerts"


class AlertService:
    def __init__(self):
        logger.info(f"✓ Alert Service initialized - Using HTTP endpoint: {JAVA_ALERT_ENDPOINT}")

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

            alert_data = {
                "patient_id": str(patient_id),
                "glucose_value": glucose_value,
                "alert_type": alert_type,
                "severity": severity,
                "message": message,
                "timestamp": timestamp_tz.isoformat(),
                "created_at": created_at_tz.isoformat()
            }

            success = self._send_to_java_backend(alert_data)
            logger.warning(f"🚨 {severity} {alert_type} alert for patient {patient_id}: {glucose_value} mg/dL")
            return success

        return False

    def _send_to_java_backend(self, alert_data: dict):
        """Send alert directly to Java backend via HTTP"""
        try:
            response = requests.post(
                JAVA_ALERT_ENDPOINT,
                json=alert_data,
                timeout=3.0
            )

            if response.status_code == 200:
                logger.info(f"✓ Alert sent to Java backend successfully (HTTP {response.status_code})")
                return True
            else:
                logger.error(f"✗ Java backend returned error: HTTP {response.status_code}")
                return False

        except requests.Timeout:
            logger.error(f"✗ HTTP request to Java backend timed out after 3s")
            return False
        except Exception as e:
            logger.error(f"✗ Failed to send alert via HTTP: {e}", exc_info=True)
            return False

_alert_service = None


def get_alert_service() -> AlertService:
    global _alert_service
    if _alert_service is None:
        _alert_service = AlertService()
    return _alert_service
