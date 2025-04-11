from config import get_algorithm_config
import requests
import json
from models import Location, LocationBase, LocationApiResponse
import uuid

class APIService:
    def __init__(self):
        self.algorithm_config = get_algorithm_config()

    def start_simulation(self):
        url = self.algorithm_config.api_host + "/control/reset"
        params = {
            "seed": self.algorithm_config.seed,
            "targetDispatches": self.algorithm_config.target_dispatches,
            "maxActiveCalls": self.algorithm_config.max_active_calls
        }

        response = requests.post(url, params=params)

        print("Status Code:", response.status_code)
        print("Response Body:", response.text)


    def stop_simulation(self):
        url = self.algorithm_config.api_host + "/control/stop"

        response = requests.post(url)

        print("Status Code:", response.status_code)
        response = requests.get(url)
        print("Response Body:", response.text)

    def next(self):
        url = self.algorithm_config.api_host + "/calls/next"

        response = requests.get(url)
        print("Status Code:", response.status_code)
        response_body = json.loads(response.text)
        print("Response Body:", response_body)

    def get_locations(self) -> list[Location]:
        url = self.algorithm_config.api_host + "/locations"

        response = requests.get(url)
        response_body = json.loads(response.text)
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

        #print(response_body)
        return locations

    def get_service(self, service_name) -> list[LocationApiResponse]:
        url = self.algorithm_config.api_host + "/" + service_name + "/search"

        response = requests.get(url)
        response_body = json.loads(response.text)
        locations = []
        for location in response_body:
            locations.append(LocationApiResponse(
                county=location["county"],
                city=location["city"],
                latitude=location["latitude"],
                longitude=location["longitude"],
                quantity=location["quantity"],
            ))

        #print(response_body)
        return locations

if __name__ == "__main__":
    import time

    api_service = APIService()
    
    api_service.start_simulation()

    # api_service.get_locations()

    # api_service.next()

    # api_service.next()

    time.sleep(3)

    # api_service.next()
    
    api_service.stop_simulation()