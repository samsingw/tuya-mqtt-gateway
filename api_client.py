import logging
import requests

logger = logging.getLogger(__name__)

class TuyaAPIClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def send_command(self, device_id, command, params):
        """
        Sends a command to the API server to control a Tuya device.
        :param device_id: The ID or name of the device.
        :param command: The DPS key or code (e.g., "switch_led", "bright_value").
        :param params: The value to set (e.g., "true", "false", 500).
        """
        if not hasattr(self, "device_name_map"):
                self.device_name_map = {}
        device_name = self.device_name_map.get(device_id, device_id)  # Fallback to device_id if no name
        url = f"{self.base_url}/set/{device_name}/{command}/{params}"
        logger.debug(f"Sending command to API: URL={url}")

        response = requests.get(url)
        logger.debug(f"API Response: {response.status_code} - {response.text}")
        response.raise_for_status()
        return response.json()

    def get_status(self, device_id):
        if not hasattr(self, "device_name_map"):
            self.device_name_map = {}
        device_name = self.device_name_map.get(device_id, device_id)  # Fallback to device_id if no name
        url = f"{self.base_url}/status/{device_name}"
        response = requests.get(url)
        response.raise_for_status()
        try:
            data = response.json()
            logger.debug(f"Status response for {device_id}: {data}")
            return data.get("dps", {})  # Return only the `dps` dictionary
        except ValueError:
            logger.error("Failed to parse status response as JSON")
            raise

    def get_devices(self):
        """Fetch device list from the API server and parse the response."""
        url = f"{self.base_url}/devices"
        response = requests.get(url)
        response.raise_for_status()
        try:
            devices = response.json()  # Parse the JSON response
            logger.debug(f"Devices response: {devices}")

            # Maintain a mapping of device_id to device_name
            self.device_name_map = {
                device["id"]: device["name"]
                for device in devices.values()
                if "id" in device and "name" in device
            }
            return devices
        except ValueError:
            logger.error("Failed to parse devices API response as JSON")
            raise

    def get_metadata(self, device_id):
        """Retrieve metadata for a specific device."""
        url = f"{self.base_url}/device/{device_id}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        logger.debug(f"Metadata for {device_id}: {data}")
        return data
