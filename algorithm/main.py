import requests
from models import Location, LocationBase
from api_service import APIService
from utils import find_locations_epicenter, rank_locations_by_distance
import uuid

class Algorithm:

    def __init__(self):
        self.locations = []
        self.ranking = []

def algorithm_handler():
    api_service = APIService()
    algorithm = Algorithm()

    api_service.start_simulation()

    algorithm.locations = api_service.get_locations()
    services = ["medical", "fire", "police", "rescue", "utility"]
    for service in services:
        locations_with_service = api_service.get_service(service)
        for location in locations_with_service:
            # Find the corresponding location in the algorithm's locations list
            for loc in algorithm.locations:
                if loc.city == location.city and loc.county == location.county:
                    setattr(loc, service, location.quantity)
                    break

    #print(algorithm.locations)
    epicenter_coords = find_locations_epicenter(algorithm.locations, "Maramureș")
    #print(f"Epicenter coordinates: {epicenter_coords}")

    epicenter = Location(
        county="Maramureș",
        city="Epicenter",
        latitude=epicenter_coords[0],
        longitude=epicenter_coords[1],
        medical=0,
        fire=0,
        police=0,
        rescue=0,
        utility=0,
        location_id=uuid.uuid4(),
    )

    algorithm.ranking = rank_locations_by_distance(epicenter, algorithm.locations)
    # print("Ranked locations:")
    # for loc in algorithm.ranking:
    #     print(f"Location: {loc.city}, County: {loc.county}")

    api_service.stop_simulation()
    # run algo
if __name__ == "__main__":
    algorithm_handler()

    # cleanup etc.

