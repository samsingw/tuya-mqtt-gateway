# config.py

MQTT_BROKER = "emqx.ankhmorpork.dw"
MQTT_PORT = 1883
MQTT_USERNAME = "tuya-mqtt-gw"
MQTT_PASSWORD = "wf6nG2?ATb=d6lHI{0"

API_SERVER_BASE_URL = "http://localhost:8888"  # URL of the tinytuya API server

MQTT_COMMAND_TOPIC_TEMPLATE = "homie/{device_id}/data/{property}/set"
MQTT_STATUS_TOPIC_TEMPLATE = "homie/{device_id}/data/{property}"

LOG_LEVEL = "DEBUG"
