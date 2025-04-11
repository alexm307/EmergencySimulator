from models import Location
import math

def calculate_location_distance(loc1: Location, loc2: Location) -> float:
    """
    Calculate the Euclidean distance between two locations based on their latitude and longitude.

    Parameters:
        loc1 (Location): The first location.
        loc2 (Location): The second location.
    
    Returns:
        float: The Euclidean distance (in degrees) between the two locations.
    """
    lat_diff = loc2.latitude - loc1.latitude
    lon_diff = loc2.longitude - loc1.longitude
    
    distance = math.sqrt(lat_diff ** 2 + lon_diff ** 2)
    return distance


def calculate_cost(central_location, source_location, dest_location):
    """
    Calculate the cost for sending service outside critical zone
    """
    dist_for_help = calculate_location_distance(source_location, dest_location)
    dist_to_center = calculate_location_distance(central_location, source_location)

    return dist_for_help - dist_to_center

def find_locations_epicenter(locations: list["Location"], county: str) -> list[float]:
    """
    Find the epicenter of the locations based on their latitude and longitude.

    Parameters:
        locations (list[Location]): A list of Location objects.
        county (str): The county to filter locations by.

    Returns:
        list[float]: A list containing the latitude and longitude of the epicenter.
                     Returns [0.0, 0.0] if no locations match the given county.
    """
    lat_sum = 0.0
    lon_sum = 0.0
    locations_counted = 0

    for loc in locations:
        if loc.county == county:
            lat_sum += loc.latitude
            lon_sum += loc.longitude
            locations_counted += 1

    if locations_counted == 0:
        return [0.0, 0.0]

    return [lat_sum / locations_counted, lon_sum / locations_counted]

def rank_locations_by_distance(central: Location, locations: list[Location]) -> list[Location]:
    """
    Calculate the Euclidean distance of each location from a central location and return a
    list of locations sorted by the distance in ascending order.

    Parameters:
        central (Location): The central reference location.
        locations (list[Location]): A list of other locations to rank.

    Returns:
        list[Location]: A list of locations ordered from the closest to the farthest.
    """
    distance_list = []

    for loc in locations:
        distance = calculate_location_distance(central, loc)
        if loc.police == 0 and loc.fire == 0 and loc.rescue == 0 and loc.utility == 0 and loc.medical == 0:
            #print(loc.city)
            continue # skip locations without any service
        distance_list.append((loc, distance))

    ranked_locations = sorted(distance_list, key=lambda item: item[1])
    return [loc for loc, _ in ranked_locations]

def process_city(city:Location):
    if city.county == "Maramures":
        pass