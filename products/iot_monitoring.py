import random
from datetime import datetime


# Permitted temperature range for this demonstration
MIN_TEMPERATURE = 2.0
MAX_TEMPERATURE = 8.0


def generate_temperature_reading():
    """
    Simulate a temperature reading from an IoT sensor.
    This is a demonstration, not a connection to a real sensor.
    """
    temperature = round(random.uniform(0.0, 12.0), 2)

    if MIN_TEMPERATURE <= temperature <= MAX_TEMPERATURE:
        status = "NORMAL"
        message = "Temperature is within the permitted range."
    else:
        status = "ALERT"
        message = "Temperature anomaly detected! Check storage conditions."

    return {
        "temperature": temperature,
        "status": status,
        "message": message,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "minimum": MIN_TEMPERATURE,
        "maximum": MAX_TEMPERATURE,
    }