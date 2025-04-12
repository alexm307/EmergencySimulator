from models import Location, LocationBase, EmergencyLocation
import math
from api_service import APIService

def calculate_location_distance(loc1: LocationBase, loc2: LocationBase) -> float:
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

def rank_locations_by_distance(central: Location, locations: list[Location], api_service: APIService) -> list[Location]:
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
        police = api_service.get_service_for_city("police", loc.city, loc.county)
        fire = api_service.get_service_for_city("fire", loc.city, loc.county)
        rescue = api_service.get_service_for_city("rescue", loc.city, loc.county)
        utility = api_service.get_service_for_city("utility", loc.city, loc.county)
        medical = api_service.get_service_for_city("medical", loc.city, loc.county)
        if police == 0 and fire == 0 and rescue == 0 and utility == 0 and medical == 0:
            #print(loc.city)
            continue # skip locations without any service
        distance_list.append((loc, distance))

    ranked_locations = sorted(distance_list, key=lambda item: item[1])
    return [loc for loc, _ in ranked_locations]

def rank_external_suppliers(central:LocationBase, city_in_need:Location, locations: list[Location]) -> list[Location]:
    """
    Create a ranked list of most cost-effective locations to check for resources based on a cost function.
    """
    cost_list = []
    for loc in locations:
        cost = calculate_cost(central, city_in_need, loc)
        cost_list.append((loc, cost))
    ranked_external_suppliers = sorted(cost_list, key=lambda item: item[1])
    return [loc for loc, _ in ranked_external_suppliers]

def solve_emergency(central: LocationBase, emergency_location: LocationBase, supply_locations_sorted: list[Location], api_service: APIService) -> bool:
    if emergency_location.county == "Maramureș":
        return fulfill_emergency_needs(emergency_location, supply_locations_sorted, api_service)
    ranked_external_suppliers = rank_external_suppliers(central, emergency_location, supply_locations_sorted)
    return fulfill_emergency_needs(emergency_location, ranked_external_suppliers, api_service)


def fulfill_emergency_needs(
    emergency_location: EmergencyLocation,
    supply_locations_sorted: list[Location],
    api_service: APIService,
) -> bool:
    resource_fields = ["medical", "fire", "police", "rescue", "utility"]
    completed = True
    print("EMERGENCY LOCATION " + emergency_location.city)
    for resource_type in resource_fields:
        print("RESOURCE " + resource_type)
        needed = getattr(emergency_location, resource_type)
        if needed is None or needed <= 0:
            continue  # No need for this resource, move on
        print("NEEDED " + str(needed))
        # Try to fulfill 'needed' from the supply locations ranked by closeness to emergency
        for supplier in supply_locations_sorted:
            available = api_service.get_service_for_city(resource_type, supplier.city, supplier.county)
            print("CITY " + str(supplier.city) + " AVAILABLE " + str(available))
            if available <= 0:
                continue  # This supplier has none of this resource

            # If this supplier alone can fulfill the entire need:
            if available >= needed:
                api_service.dispatch_service_to_city(
                    resource_type,
                    supplier.city,
                    supplier.county,
                    emergency_location.city,
                    emergency_location.county,
                    needed
                )
                needed = 0
                break  # We've satisfied this resource completely

            else:
                # Supplier can provide only a part of what's needed
                api_service.dispatch_service_to_city(
                    resource_type,
                    supplier.city,
                    supplier.county,
                    emergency_location.city,
                    emergency_location.county,
                    available
                )
                needed -= available
                # Move on to the next supplier to fulfill the remainder
        if needed > 0:
            # If we exit the loop and still have unmet needs, mark as incomplete
            completed = False
            print(f"Emergency location {emergency_location.city} still needs {needed} of {resource_type}")
    return completed

def parse_emergency_location_payload(payload: dict) -> EmergencyLocation:
    """
    Convert a JSON payload into a LocationBase model instance.

    Args:
        payload (dict): The JSON object with location data.

    Returns:
        LocationBase: Populated model instance.
    """
    # 1. Extract top-level fields
    city = payload.get("city", "")
    county = payload.get("county", "")
    latitude = payload.get("latitude", 0.0)
    longitude = payload.get("longitude", 0.0)

    # 2. Initialize resource counters
    resources = {
        "medical": 0,
        "fire": 0,
        "police": 0,
        "rescue": 0,
        "utility": 0,
    }

    # 3. Define a mapping from the request "Type" to our resource fields
    type_mapping = {
        "Medical": "medical",
        "Fire": "fire",
        "Police": "police",
        "Rescue": "rescue",
        "Utility": "utility",
    }

    # 4. Go through requests and map them to our resource fields
    requests = payload.get("requests", [])
    for req in requests:
        rtype = req.get("Type", "")
        quantity = req.get("Quantity", 0)
        mapped_field = type_mapping.get(rtype)
        if mapped_field is not None:
            resources[mapped_field] = quantity

    # 5. Create the LocationBase instance
    emergency_location = EmergencyLocation(
        county=county,
        city=city,
        latitude=latitude,
        longitude=longitude,
        medical=resources["medical"],
        fire=resources["fire"],
        police=resources["police"],
        rescue=resources["rescue"],
        utility=resources["utility"]
    )

    return emergency_location
