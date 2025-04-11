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

    cost = dist_for_help - dist_to_center