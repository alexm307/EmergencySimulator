from config import get_algorithm_config
import requests
import json
from models import Location, LocationBase, LocationApiResponse
import uuid

class APIService:
    def __init__(self):
        self.algorithm_config = get_algorithm_config()

    def _send_post_request_with_retry(self, url: str, params: dict, body: dict):
        """
        Send a POST request with retry logic.
        """
        retry = self.algorithm_config.retry_count
        timeout = self.algorithm_config.timeout
        attempt = 0

        while attempt < retry:
            try:
                response = requests.post(url, params=params, timeout=timeout, json=body)

                if response.status_code == 200:
                    if response.text.strip():
                        try:
                            return json.loads(response.text)
                        except json.JSONDecodeError:
                            print("Response returned 200 but contains invalid JSON.")
                            return None
                    else:
                        print("Response returned 200 but is empty.")
                        return None
                else:
                    print(f"Attempt {attempt + 1}/{retry} failed with status code {response.status_code}")

            except requests.exceptions.Timeout:
                print(f"Attempt {attempt + 1}/{retry} timed out.")

            except requests.exceptions.RequestException as e:
                print(f"Attempt {attempt + 1}/{retry} failed due to an error: {e}")

            attempt += 1

        print(f"POST request to {url} failed after {retry} attempts.")

    def _send_get_request_with_retry(self, url: str, params: dict = None):
        """
        Send a GET request with retry logic.
        """
        retry = self.algorithm_config.retry_count
        timeout = self.algorithm_config.timeout
        attempt = 0

        while attempt < retry:
            try:
                response = requests.get(url, params=params, timeout=timeout)

                if response.status_code == 200:
                    if response.text.strip():
                        try:
                            print("Response code 200, Response text:", response.text)
                            return json.loads(response.text)
                        except json.JSONDecodeError:
                            print("Response returned 200 but contains invalid JSON.")
                            return None
                    else:
                        print("Response returned 200 but is empty.")
                        return None
                else:
                    print(f"Attempt {attempt + 1}/{retry} failed with status code {response.status_code}")

            except requests.exceptions.Timeout:
                print(f"Attempt {attempt + 1}/{retry} timed out.")

            except requests.exceptions.RequestException as e:
                print(f"Attempt {attempt + 1}/{retry} failed due to an error: {e}")

            attempt += 1

        print(f"GET request to {url} failed after {retry} attempts.")
    
    def start_simulation(self):
        url = self.algorithm_config.api_host + "/control/reset"
        params = {
            "seed": self.algorithm_config.seed,
            "targetDispatches": self.algorithm_config.target_dispatches,
            "maxActiveCalls": self.algorithm_config.max_active_calls
        }

        self._send_post_request_with_retry(url, params, None)

    def stop_simulation(self):
        url = self.algorithm_config.api_host + "/control/stop"

        return self._send_post_request_with_retry(url, None, None)

    def next(self):
        url = self.algorithm_config.api_host + "/calls/next"

        return self._send_get_request_with_retry(url)
    
    def location_exists(self, city: str, county: str, locations: list[LocationBase]) -> int:
        """
        Check if a location with the given city and county exists in the list of locations.
        """
        for index, location in enumerate(locations):
            if location.city == city and location.county == county:
                return index
        return -1

    def get_locations(self) -> list[LocationBase]:
        services = ["medical", "fire", "police", "rescue", "utility"]
        locations = []
        for service in services:
            url = self.algorithm_config.api_host + "/" + service + "/search"
            response = self._send_get_request_with_retry(url, {})
            if response is None:
                print(f"Failed to get {service} locations.")
                response = []
            
            for location in response:
                existing_index = self.location_exists(location["city"], location["county"], locations)
                if existing_index == -1:
                    locations.append(LocationBase(
                        location_id=uuid.uuid4(),
                        county=location["county"],
                        city=location["city"],
                        latitude=location["latitude"],
                        longitude=location["longitude"],
                    ))

        return locations

    def get_service_for_city(self, service_name, city, county) -> int:
        url = self.algorithm_config.api_host + "/" + service_name + "/searchbycity"
        params = {
            "city": city,
            "county": county
        }
        response = self._send_get_request_with_retry(url, params)
        if response is None:
            return 0
        return max(response,0)
    
    def dispatch_service_to_city(self, service_name, source_city, source_county, target_city, target_county, quantity):
        url = self.algorithm_config.api_host + "/" + service_name + "/dispatch"
        body = {
            "sourceCity": source_city,
            "sourceCounty": source_county,
            "targetCity": target_city,
            "targetCounty": target_county,
            "quantity": quantity
        }
        response = self._send_post_request_with_retry(url, None, body)
        return response