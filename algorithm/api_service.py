from config import get_algorithm_config
import requests
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
        print("Response Body:", response.text)

if __name__ == "__main__":
    import time

    api_service = APIService()
    
    api_service.start_simulation()

    time.sleep(3)

    api_service.stop_simulation()