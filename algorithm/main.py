import requests
from models import Location, LocationBase
from api_service import APIService
from utils import find_locations_epicenter, rank_locations_by_distance, parse_emergency_location_payload, solve_emergency
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
    # for service in services:
    #     for location in algorithm.locations:
    #         quantity = api_service.get_service_for_city(service, location.city, location.county)
    #         setattr(location, service, quantity)

    epicenter_coords = find_locations_epicenter(algorithm.locations, "Maramureș")
    #print(f"Epicenter coordinates: {epicenter_coords}")

    epicenter = LocationBase(
        county="Maramureș",
        city="Epicenter",
        latitude=epicenter_coords[0],
        longitude=epicenter_coords[1],
        # medical=0,
        # fire=0,
        # police=0,
        # rescue=0,
        # utility=0,
    )

    algorithm.ranking = rank_locations_by_distance(epicenter, algorithm.locations, api_service)
    # for location in algorithm.ranking:
    #     print(f"Location: {location.city}, County: {location.county}, Medical: {location.medical}, Fire: {location.fire}, Police: {location.police}, Rescue: {location.rescue}, Utility: {location.utility}")
    
    emergency = api_service.next()
    # idx = 0
    while emergency is not None:
        emergency_processed = parse_emergency_location_payload(emergency)
        [indices_to_remove, completed] = solve_emergency(epicenter, emergency_processed, algorithm.ranking, api_service)
        print(f"Emergency completed: {completed}")
        new_ranking = algorithm.ranking.copy()
        for i in sorted(indices_to_remove, reverse=True):
            del new_ranking[i]
        algorithm.ranking = new_ranking
        # print(idx)
        # if emergency_processed.county != "Maramureș":
        #     print(f"Emergency: {emergency_processed}")
        # idx = idx + 1
        emergency = api_service.next()

    response = api_service.stop_simulation()
    print(response)

if __name__ == "__main__":
    algorithm_handler()
