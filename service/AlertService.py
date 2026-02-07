import json
import logging
from datetime import datetime
from uuid import UUID
from zoneinfo import ZoneInfo

from google.cloud import pubsub_v1
from config.Settings import settings

logger = logging.getLogger(__name__)

# Europe/Warsaw timezone
WARSAW_TZ = ZoneInfo("Europe/Warsaw")


class AlertService:
    def __init__(self):
        # Configure publisher with batch settings for immediate publishing
        batch_settings = pubsub_v1.types.BatchSettings(
            max_bytes=1024,  # 1KB - small batch size
            max_latency=0.1,  # 100ms max delay
            max_messages=1,  # Publish immediately with single message
        )
        self.publisher = pubsub_v1.PublisherClient(batch_settings=batch_settings)
        self.topic_path = self.publisher.topic_path(
            settings.gcp_project_id,
            settings.pubsub_topic
        )
        logger.info(f"✓ Alert Service initialized - Topic: {self.topic_path}")

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

            self._send_to_pubsub(alert_data)
            logger.warning(f"🚨 {severity} {alert_type} alert for patient {patient_id}: {glucose_value} mg/dL")
            return True

        return False

    def _send_to_pubsub(self, alert_data: dict):
        try:
            message_json = json.dumps(alert_data)
            message_bytes = message_json.encode('utf-8')

            future = self.publisher.publish(self.topic_path, message_bytes)
            # Increased timeout and added retry logic
            try:
                message_id = future.result(timeout=30)
                logger.info(f"✓ Alert published to Pub/Sub (Message ID: {message_id})")
                return message_id
            except TimeoutError:
                logger.error(f"✗ Pub/Sub publish timed out after 30s. Message may still be delivered.")
                # Don't raise, allow the job to continue
                return None

        except Exception as e:
            logger.error(f"✗ Failed to publish alert to Pub/Sub: {e}")
            # Don't raise the exception to prevent blocking glucose readings
            return None

_alert_service = None


def get_alert_service() -> AlertService:
    global _alert_service
    if _alert_service is None:
        _alert_service = AlertService()
    return _alert_service
