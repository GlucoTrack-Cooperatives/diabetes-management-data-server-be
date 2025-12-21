import logging

from pydexcom import Dexcom, Region
from pydexcom.errors import AccountError

from dao.model.User import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def authenticate(username: str, password: str) -> bool:
    try:
        dexcom = Dexcom(
            username=username,
            password=password,
            region=Region.OUS
        )
        reading = dexcom.get_current_glucose_reading()
        return True
    except AccountError as e:
        print(f"✗ Authentication failed: {e}")
        return False


def get_current_glucose(user: User):
    dexcom = Dexcom(
        username=user.dexcom_email,
        password=user.dexcom_password,
        region=Region.OUS
    )

    reading = dexcom.get_current_glucose_reading()
    if reading is None:
        return None

    return {
        "value": reading.value,
        "trend": str(reading.trend),
        "timestamp": reading.datetime.strftime("%Y-%m-%d %H:%M:%S")
    }
