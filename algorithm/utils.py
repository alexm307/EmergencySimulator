from models import Location, LocationBase
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

def rank_external_suppliers(central:Location, city_in_need:Location, locations: list[Location]) -> list[Location]:
    """
    """
    cost_list = []
    for loc in locations:
        cost = calculate_cost(central, city_in_need, loc)
        cost_list.append((loc, cost))
    ranked_external_suppliers = sorted(cost_list, key=lambda item: item[1])
    return [loc for loc, _ in ranked_external_suppliers]

def solve_emergency(emergency_location: LocationBase, supply_locations_sorted: list[Location]):
    if emergency_location.county == "Maramureș":
        fulfill_internal_needs(emergency_location, supply_locations_sorted)
    fulfill_external_needs(emergency_location, supply_locations_sorted)


def fulfill_external_needs(
    city_in_need: LocationBase,
    supply_locations_sorted: list[Location]): 
    """
    """
    

    


def fulfill_internal_needs(
    city_in_need: LocationBase,
    supply_locations_sorted: list[Location]
) -> bool:

    # The resource fields we want to check
    resource_fields = ["medical", "fire", "police", "rescue", "utility"]
    
    for resource_type in resource_fields:
        needed = getattr(city_in_need, resource_type)
        if needed is None or needed <= 0:
            continue  # No need for this resource, move on
        
        # Try to fulfill 'needed' from the supply locations
        for supplier in supply_locations_sorted:
            #TODO: add getByCity
            available = getattr(supplier, resource_type)
            if available <= 0:
                continue  # This supplier has none of this resource

            # If this supplier alone can fulfill the entire need:
            if available >= needed:
                setattr(supplier, resource_type, available - needed)
                needed = 0
                #TODO: dispatch post request
                break  # We've satisfied this resource completely

            else:
                # Supplier can provide only a part of what's needed
                setattr(supplier, resource_type, 0)
                needed -= available
                #TODO: dispatch post request
                # Move on to the next supplier to fulfill the remainder
    
    # If we reach here, all resources have been successfully fulfilled
    return True
