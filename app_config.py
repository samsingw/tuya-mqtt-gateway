import sys
import os

# Add the config folder to the Python path dynamically
sys.path.append(os.path.join(os.path.dirname(__file__), "config"))
# Import the dynamically loaded config
from config import config

# Extract configuration values
API_SERVER = config.API_SERVER
MQTT_BROKER = config.MQTT_BROKER
MQTT_PORT = config.MQTT_PORT
MQTT_USERNAME = config.MQTT_USERNAME
MQTT_PASSWORD = config.MQTT_PASSWORD
MQTT_COMMAND_TOPIC_TEMPLATE = config.MQTT_COMMAND_TOPIC_TEMPLATE
MQTT_STATUS_TOPIC_TEMPLATE = config.MQTT_STATUS_TOPIC_TEMPLATE
PRODUCT_CONFIG_FILE = config.PRODUCT_CONFIG_FILE
LOG_LEVEL = config.LOG_LEVEL
