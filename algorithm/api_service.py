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
        Parameters:
            url (str): The URL to send the request to.
            params (dict): The parameters to include in the request.
            retry (int): The number of retry attempts.
            timeout (float): The timeout for each request in seconds.
        """
        retry = self.algorithm_config.retry_count
        timeout = self.algorithm_config.timeout
        attempt = 0

        while attempt < retry:
            try:
                response = requests.post(url, params=params, timeout=timeout, json=body)

                if response.status_code == 200:
                    return  json.loads(response.text)
                else:
                    print(f"Attempt {attempt + 1}/{retry} failed with status code {response.status_code}")
            
            except requests.exceptions.Timeout:
                print(f"Attempt {attempt + 1}/{retry} timed out.")

            except requests.exceptions.RequestException as e:
                print(f"Attempt {attempt + 1}/{retry} failed due to an error: {e}")

            attempt += 1
        print(f"Request failed after {retry} attempts.")

    def _send_get_request_with_retry(self, url: str, params: dict = None):
        """
        Send a GET request with retry logic.
        
        Parameters:
            url (str): The URL to send the request to.
            params (dict): The parameters to include in the request.

        Returns:
            dict: The JSON-decoded response body if the request is successful.

        Raises:
            RuntimeError: If all retry attempts fail.
        """
        retry = self.algorithm_config.retry_count
        timeout = self.algorithm_config.timeout
        attempt = 0

        while attempt < retry:
            try:
                response = requests.get(url, params=params, timeout=timeout)

                if response.status_code == 200:
                    #print("RESPONSE TEXT: ", response.text)
                    return json.loads(response.text)
                else:
                    print(f"Attempt {attempt + 1}/{retry} failed with status code {response.status_code}")

            except requests.exceptions.Timeout:
                print(f"Attempt {attempt + 1}/{retry} timed out.")

            except requests.exceptions.RequestException as e:
                print(f"Attempt {attempt + 1}/{retry} failed due to an error: {e}")

            attempt += 1

        raise RuntimeError(f"GET request to {url} failed after {retry} attempts.")
    
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

    def get_locations(self) -> list[Location]:
        url = self.algorithm_config.api_host + "/locations"

        response_body = self._send_get_request_with_retry(url)
        locations = []
        for location in response_body:
            locations.append(Location(
                location_id=uuid.uuid4(),
                county=location["county"],
                city=location["name"],
                latitude=location["lat"],
                longitude=location["long"],
                medical=0,
                fire=0,
                police=0,
                rescue=0,
                utility=0,
            ))

        return locations

    def get_service_for_city(self, service_name, city, county) -> list[LocationApiResponse]:
        url = self.algorithm_config.api_host + "/" + service_name + "/searchbycity"
        params = {
            "city": city,
            "county": county
        }
        response = self._send_get_request_with_retry(url, params)
        if county != "Maramureș":
            pass
            #print(f"Service name: {service_name}, City: {city}, County: {county}, Response: {response}")
        
        return response
if __name__ == "__main__":
    import time

    api_service = APIService()
    
    api_service.start_simulation()

    locations = api_service.get_locations()
    print(locations)
    # api_service.next()

    # api_service.next()

    time.sleep(3)

    # api_service.next()
    
    api_service.stop_simulation()