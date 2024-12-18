import logging
import threading
import time
from mqtt_handler import MQTTHandler, setup_mqtt
from api_client import TuyaAPIClient
from config import API_SERVER, MQTT_BROKER, LOG_LEVEL, PRODUCT_CONFIG_FILE

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def poll_device_status(api_client, mqtt_handler):
    logger.info("Starting device status polling...")
    while True:
        try:
            devices = api_client.get_devices()
            for device_id, device in devices.items():
                logger.debug(f"Polling status for device {device_id}")
                status = api_client.get_status(device_id)
                mqtt_handler.publish_status(device_id, status)
        except Exception as e:
            logger.error(f"Error polling device status: {e}")
        time.sleep(5)

if __name__ == "__main__":
    logger.info("Starting Tuya MQTT Gateway")

    try:
        # Initialize the API client
        api_client = TuyaAPIClient(base_url=API_SERVER)

        # Initialize MQTT client and handler
        mqtt_client, mqtt_handler = setup_mqtt(
            api_client=api_client,
            product_config_file=PRODUCT_CONFIG_FILE
        )

        # Start metadata publishing for devices
        mqtt_handler.start_devices()
        logger.info("Tuya MQTT Gateway is running.")

        # Start polling device status in a background thread
        polling_thread = threading.Thread(
            target=poll_device_status,
            args=(api_client, mqtt_handler),
            daemon=True
        )
        polling_thread.start()

        # Keep the main thread running
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Shutting down Tuya MQTT Gateway...")
