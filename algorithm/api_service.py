import logging
from config import get_algorithm_config
import requests
import json
import uuid
from models import LocationBase

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class APIService:
    """
    Handles HTTP communication with the external API, including retries and dispatch logic.
    """

    def __init__(self):
        self.algorithm_config = get_algorithm_config()
        self.token = None
        self.refresh_token_value = None

    def authenticate(self):
        """
        Authenticate with the API and retrieve the token.
        """
        url = f"{self.algorithm_config.api_host}/auth/login"
        body = {"username": "distancify", "password": "hackathon"}
        response = requests.post(url, json=body)
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("token")
            self.refresh_token_value = data.get("refreshToken")
            logger.info("Authentication successful.")
        else:
            logger.error(f"Failed to authenticate: {response.status_code} - {response.text}")

    def refresh_token(self):
        """
        Refresh the authentication token using the refresh token.
        """
        url = f"{self.algorithm_config.api_host}/auth/refreshToken"
        headers = {"refresh_token": self.refresh_token_value}
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("token")
            self.refresh_token_value = data.get("refreshToken")
            logger.info("Token refreshed.")
        else:
            logger.error(f"Failed to refresh token: {response.status_code} - {response.text}")

    def _auth_headers(self):
        """
        Generate headers for authentication.
        Returns:
            dict: Headers with authorization token.
        """
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    def _send_post_request_with_retry(self, url: str, params: dict, body: dict):
        """
        Send a POST request with retry logic.

        Args:
            url (str): The request URL.
            params (dict): Query parameters.
            body (dict): JSON body payload.

        Returns:
            dict or None: Parsed response or None if failed.
        """
        retry = self.algorithm_config.retry_count
        timeout = self.algorithm_config.timeout

        for attempt in range(retry):
            try:
                response = requests.post(url, params=params, timeout=timeout, json=body, headers=self._auth_headers())
                if response.status_code == 404:
                    self.refresh_token()
                    continue
                if response.status_code == 200:
                    if response.text.strip():
                        try:
                            return json.loads(response.text)
                        except json.JSONDecodeError:
                            logger.warning("Response returned 200 but contains invalid JSON.")
                            return None
                    else:
                        logger.warning("Response returned 200 but is empty.")
                        return None
                else:
                    logger.warning(f"Attempt {attempt + 1}/{retry} failed with status code {response.status_code}")
            except requests.exceptions.Timeout:
                logger.warning(f"Attempt {attempt + 1}/{retry} timed out.")
            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt + 1}/{retry} failed due to an error: {e}")

        logger.error(f"POST request to {url} failed after {retry} attempts.")
        return None

    def _send_get_request_with_retry(self, url: str, params: dict = None):
        """
        Send a GET request with retry logic.

        Args:
            url (str): The request URL.
            params (dict): Query parameters.

        Returns:
            dict or None: Parsed response or None if failed.
        """
        retry = self.algorithm_config.retry_count
        timeout = self.algorithm_config.timeout

        for attempt in range(retry):
            try:
                response = requests.get(url, params=params, timeout=timeout, headers=self._auth_headers())
                if response.status_code == 401:
                    self.refresh_token()
                    continue
                if response.status_code == 200:
                    if response.text.strip():
                        try:
                            logger.debug(f"Response 200: {response.text}")
                            return json.loads(response.text)
                        except json.JSONDecodeError:
                            logger.warning("Response returned 200 but contains invalid JSON.")
                            return None
                    else:
                        logger.warning("Response returned 200 but is empty.")
                        return None
                else:
                    logger.warning(f"Attempt {attempt + 1}/{retry} failed with status code {response.status_code}")
            except requests.exceptions.Timeout:
                logger.warning(f"Attempt {attempt + 1}/{retry} timed out.")
            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt + 1}/{retry} failed due to an error: {e}")

        logger.error(f"GET request to {url} failed after {retry} attempts.")
        return None

    def start_simulation(self):
        """Initialize a new simulation run."""
        url = f"{self.algorithm_config.api_host}/control/reset"
        params = {
            "seed": self.algorithm_config.seed,
            "targetDispatches": self.algorithm_config.target_dispatches,
            "maxActiveCalls": self.algorithm_config.max_active_calls,
        }
        self._send_post_request_with_retry(url, params, None)

    def stop_simulation(self):
        """Stop the simulation run."""
        url = f"{self.algorithm_config.api_host}/control/stop"
        return self._send_post_request_with_retry(url, None, None)

    def next(self):
        """Get the next emergency call."""
        url = f"{self.algorithm_config.api_host}/calls/next"
        return self._send_get_request_with_retry(url)

    def location_exists(self, city: str, county: str, locations: list[LocationBase]) -> int:
        """
        Check if a location exists in the list.

        Args:
            city (str): City name.
            county (str): County name.
            locations (list[LocationBase]): List of locations.

        Returns:
            int: Index of location if exists, otherwise -1.
        """
        for index, location in enumerate(locations):
            if location.city == city and location.county == county:
                return index
        return -1

    def get_locations(self) -> list[LocationBase]:
        """
        Fetch all locations with any available emergency services.

        Returns:
            list[LocationBase]: Unique locations.
        """
        services = ["medical", "fire", "police", "rescue", "utility"]
        locations = []
        for service in services:
            url = f"{self.algorithm_config.api_host}/{service}/search"
            response = self._send_get_request_with_retry(url, {})
            if response is None:
                logger.warning(f"Failed to get {service} locations.")
                continue

            for location in response:
                if self.location_exists(location["city"], location["county"], locations) == -1:
                    locations.append(LocationBase(
                        location_id=uuid.uuid4(),
                        county=location["county"],
                        city=location["city"],
                        latitude=location["latitude"],
                        longitude=location["longitude"],
                    ))

        return locations

    def get_service_for_city(self, service_name: str, city: str, county: str) -> int:
        """
        Get quantity of a specific service type available in a city.

        Args:
            service_name (str): Service type (e.g. medical).
            city (str): City name.
            county (str): County name.

        Returns:
            int: Quantity of service available.
        """
        url = f"{self.algorithm_config.api_host}/{service_name}/searchbycity"
        params = {"city": city, "county": county}
        response = self._send_get_request_with_retry(url, params)
        if response is None:
            return 0
        return max(response, 0)

    def dispatch_service_to_city(
        self, service_name: str, source_city: str, source_county: str, target_city: str, target_county: str, quantity: int
    ):
        """
        Dispatch a given quantity of service from a source to a target location.

        Args:
            service_name (str): Type of service.
            source_city (str): Source city.
            source_county (str): Source county.
            target_city (str): Target city.
            target_county (str): Target county.
            quantity (int): Quantity to dispatch.

        Returns:
            dict or None: Response from the dispatch API.
        """
        url = f"{self.algorithm_config.api_host}/{service_name}/dispatch"
        body = {
            "sourceCity": source_city,
            "sourceCounty": source_county,
            "targetCity": target_city,
            "targetCounty": target_county,
            "quantity": quantity
        }
        return self._send_post_request_with_retry(url, None, body)