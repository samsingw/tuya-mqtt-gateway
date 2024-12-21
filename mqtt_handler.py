import logging
from paho.mqtt.client import Client
import json
import os
from config.config import MQTT_BROKER, MQTT_PORT, MQTT_USERNAME, MQTT_PASSWORD, MQTT_STATUS_TOPIC_TEMPLATE, MQTT_COMMAND_TOPIC_TEMPLATE

logger = logging.getLogger(__name__)

class MQTTHandler:
    def __init__(self, mqtt_client, api_client, product_config_file):
        self.mqtt_client = mqtt_client
        self.api_client = api_client
        self.product_config = self._load_product_config(product_config_file)

    def _load_product_config(self, product_config_file):
        """Load product-specific configuration from a JSON file."""
        cwd = os.path.dirname(__file__)
        p_conf=os.path.join(cwd,product_config_file)
        try:
            with open(p_conf, "r") as f:
                product_config = json.load(f)
                logger.info("Product configuration loaded successfully.")
                return product_config
        except Exception as e:
            logger.error(f"Error loading product configuration: {e}")
            return {"default": {"nodes": {"default": "ALL"}}}

    def get_nodes_for_device(self, product_name):
        """Get node mapping for the given product name or fall back to default."""
        return self.product_config.get(product_name, self.product_config["default"])["nodes"]

    def assign_properties_to_nodes(self, product_name, properties):
        """Assign properties to nodes based on product configuration."""
        nodes = self.get_nodes_for_device(product_name)
        node_properties = {}

        for prop_code, prop_data in properties.items():
            assigned = False
            for node, props in nodes.items():
                if props == "ALL" or prop_code in props:
                    node_properties.setdefault(node, []).append((prop_code, prop_data))
                    assigned = True
                    break

            # Unassigned properties go to the default node
            if not assigned:
                node_properties.setdefault("default", []).append((prop_code, prop_data))

        return node_properties

    def publish_metadata(self, device_id, product_name, properties):
        """Publish metadata for the device using the product configuration or default."""
        node_properties = self.assign_properties_to_nodes(product_name, properties)

        for node, props in node_properties.items():
            # Publish node metadata
            self.mqtt_client.publish(f"homie/{device_id}/{node}/$name", node.capitalize(), retain=True)
            self.mqtt_client.publish(f"homie/{device_id}/{node}/$type", "default" if node == "default" else node, retain=True)

            # Publish property metadata
            for prop_code, prop_data in props:
                self.mqtt_client.publish(f"homie/{device_id}/{node}/{prop_code}/$name", prop_data["code"], retain=True)
                self.mqtt_client.publish(f"homie/{device_id}/{node}/{prop_code}/$datatype", prop_data["type"], retain=True)
                self.mqtt_client.publish(f"homie/{device_id}/{node}/{prop_code}/$settable", "true", retain=True)

            # Publish property initial state
            for prop_code, prop_data in props:
                initial_value = prop_data.get("value", "unknown")
                self.mqtt_client.publish(f"homie/{device_id}/{node}/{prop_code}", initial_value, retain=True)

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
            device_name = topic_parts[1]
            property_name = topic_parts[3]
            command_value = msg.payload.decode("utf-8").strip()

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
        device_name = self.api_client.device_name_map.get(device_id, device_id)
        for property, value in status.items():
            topic = MQTT_STATUS_TOPIC_TEMPLATE.format(device_id=device_name, property=property)
            if not isinstance(value, (str, int, float, bytearray)):
                value = str(value)
            self.mqtt_client.publish(topic, value)
            logger.info(f"Published status to {topic}: {value}")

    def start_devices(self):
        """Fetch devices and publish metadata."""
        devices = self.api_client.get_devices()
        for device_id, device_info in devices.items():
            product_name = device_info.get("product_name", "default")
            properties = device_info.get("properties", {})
            self.publish_metadata(device_id, product_name, properties)

def setup_mqtt(api_client, product_config_file):
    mqtt_client = Client()
    mqtt_handler = MQTTHandler(mqtt_client, api_client, product_config_file)

    mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    mqtt_client.on_connect = mqtt_handler.on_connect
    mqtt_client.on_message = mqtt_handler.on_message

    mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
    mqtt_client.loop_start()

    return mqtt_client, mqtt_handler
