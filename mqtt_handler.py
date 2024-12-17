import logging
from paho.mqtt.client import Client
from config import MQTT_BROKER, MQTT_PORT, MQTT_USERNAME, MQTT_PASSWORD, MQTT_STATUS_TOPIC_TEMPLATE, MQTT_COMMAND_TOPIC_TEMPLATE

logger = logging.getLogger(__name__)

class MQTTHandler:
    def __init__(self, mqtt_client, api_client):
        self.mqtt_client = mqtt_client
        self.api_client = api_client

    def on_connect(self, client, userdata, flags, rc):
        logger.info("Connected to MQTT broker")
        client.subscribe(MQTT_COMMAND_TOPIC_TEMPLATE.format(device_id="+", property="+"))

    def on_message(self, client, userdata, msg):
        logger.info(f"Received MQTT message: {msg.topic} -> {msg.payload}")
        try:
            # Parse topic and payload
            topic_parts = msg.topic.split("/")
            if len(topic_parts) < 4:
                logger.error(f"Invalid topic format: {msg.topic}")
                return
            
            # Extract device_name and property_name from the topic
            device_name = topic_parts[1]  # Assuming topic is: homie/{device_name}/data/{property}/set
            property_name = topic_parts[3]  # Extract property from topic
            command_value = msg.payload.decode("utf-8").strip()  # Decode the value
            
            # Map device_name back to device_id
            device_id = next((k for k, v in self.api_client.device_name_map.items() if v == device_name), None)
            if not device_id:
                logger.error(f"Device name '{device_name}' not found in mapping.")
                return

            # Send the command to the API server
            self.api_client.send_command(device_id, property_name, command_value)
            logger.info(f"Command sent to {device_name} ({device_id}): {property_name} -> {command_value}")
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")

    def publish_status(self, device_id, status):
        device_name = self.api_client.device_name_map.get(device_id, device_id)  # Use device_name
        for property, value in status.items():
            topic = MQTT_STATUS_TOPIC_TEMPLATE.format(device_id=device_name, property=property)
            if not isinstance(value, (str, int, float, bytearray)):  # Serialize complex data
                value = str(value)
            self.mqtt_client.publish(topic, value)
            logger.info(f"Published status to {topic}: {value}")

    def publish_metadata(self):
          """Fetch and publish metadata for all devices."""
          devices = self.api_client.get_devices()  # Assuming get_devices() returns all devices
          for device_id, device_info in devices.items():
              # Extract metadata
              device_name = device_info["name"]
              nodes = ["light"]  # Example node type
              # Publish device metadata
              self.mqtt_client.publish(f"homie/{device_id}/$homie", "4.0.0", retain=True)
              self.mqtt_client.publish(f"homie/{device_id}/$name", device_name, retain=True)
              self.mqtt_client.publish(f"homie/{device_id}/$label", device_name, retain=True)
              self.mqtt_client.publish(f"homie/{device_id}/$state", "ready", retain=True)
              self.mqtt_client.publish(f"homie/{device_id}/$nodes", ",".join(nodes), retain=True)

              # Publish node and property metadata (if applicable)
              self.mqtt_client.publish(f"homie/{device_id}/light/$name", "Light Control", retain=True)
              self.mqtt_client.publish(f"homie/{device_id}/light/$type", "switch", retain=True)
              self.mqtt_client.publish(f"homie/{device_id}/light/power/$name", "Power", retain=True)
              self.mqtt_client.publish(f"homie/{device_id}/light/power/$datatype", "boolean", retain=True)
              self.mqtt_client.publish(f"homie/{device_id}/light/power/$settable", "true", retain=True)

def setup_mqtt(api_client):
    mqtt_client = Client()
    mqtt_handler = MQTTHandler(mqtt_client, api_client)

    mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    mqtt_client.on_connect = mqtt_handler.on_connect
    mqtt_client.on_message = mqtt_handler.on_message

    mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
    mqtt_client.loop_start()

    return mqtt_client, mqtt_handler
