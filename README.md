# Tuya MQTT Gateway

The **Tuya MQTT Gateway** bridges Tuya-compatible IoT devices with an MQTT broker using the Homie convention, enabling seamless integration with platforms like OpenHAB. The gateway retrieves device metadata and statuses from a Tuya API server, publishes them to MQTT, and handles commands sent from the MQTT broker.

## Features
- **Homie 4.0.0 Compliance**: Auto-discovery and structured topic hierarchy for OpenHAB integration.
- **Device Management**: Fetch device metadata and statuses from the Tuya API server.
- **Dynamic Node Mapping**: Supports product-specific configurations via `products.json`.
- **Default Node Handling**: Groups unmapped or unknown properties into a fallback `default` node.
- **Resilient Command Handling**: Executes commands from MQTT broker and updates device states.

---

## Requirements

### Hardware
- Tuya-compatible devices
- A running MQTT broker
- A running tinytuya server (https://github.com/jasonacox/tinytuya/tree/master/server)
 
### Software
- Python 3.8+
- `paho-mqtt`: MQTT client library
- `requests`: HTTP library
- `homie-spec`: Python Library that models the v4 Homie Convention.

---

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/<your-repo>/tuya-mqtt-gateway.git
   cd tuya-mqtt-gateway
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the Gateway**:
   Edit `config.py`:
   ```python
   API_SERVER = "http://<tuya-api-server-url>:<port>"
   MQTT_BROKER = {"host": "<mqtt-broker-host>", "port": <mqtt-port>, "username": "<mqtt-username>", "password": "<mqtt-password>"}
   PRODUCT_CONFIG_FILE = "products.json"
   LOG_LEVEL = "INFO"
   ```

4. **Prepare `products.json`**:
   Create or update the `products.json` file to define node-property mappings for each product type. Example:
   ```json
   {
     "default": {
       "nodes": {
         "default": "ALL"
       }
     },
     "prios_g9_cct": {
       "nodes": {
         "light_control": ["switch_led", "bright_value", "temp_value"],
         "feature_control": ["work_mode", "countdown", "scene_data"]
       }
     }
   }
   ```

---

## Usage

### Start the Gateway
Run the following command to start the gateway:
```bash
python tuya_mqtt_gw.py
```

### Logs
Monitor the gateway logs to ensure proper operation:
```bash
tail -f logs/tuya_mqtt_gw.log
```

---

## How It Works
1. **Metadata Publishing**:
   - The gateway fetches device metadata and publishes Homie-compliant topics to the MQTT broker.

2. **Auto-Discovery**:
   - OpenHAB detects devices based on the Homie topics.

3. **Command Execution**:
   - Commands from the MQTT broker are routed to the Tuya API server.

4. **Device Status Polling**:
   - The gateway periodically polls the Tuya API server for device status updates.

---

## Contributing
Feel free to submit issues and pull requests to enhance the project.

---

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
