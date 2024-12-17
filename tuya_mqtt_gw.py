import logging
import time
from mqtt_handler import MQTTHandler, setup_mqtt
from api_client import TuyaAPIClient
from config import API_SERVER_BASE_URL, LOG_LEVEL

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def poll_device_status(api_client, mqtt_handler):
    while True:
        try:
            devices = api_client.get_devices()
            for device_id, device in devices.items():  # Iterate over dictionary items
                status = api_client.get_status(device_id)
                mqtt_handler.publish_status(device_id, status)
        except Exception as e:
                logger.error(f"Error polling device status: {e}")
        time.sleep(5)


if __name__ == "__main__":
    logger.info("Starting Tuya MQTT Gateway")

    # Initialize the API client
    api_client = TuyaAPIClient(base_url=API_SERVER_BASE_URL)

    # Set up MQTT
    mqtt_client, mqtt_handler = setup_mqtt(api_client)
    mqtt_handler.publish_metadata()

    # Poll device status in the background
    poll_device_status(api_client, mqtt_handler)
