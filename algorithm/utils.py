import math
import logging
from models import Location, LocationBase, EmergencyLocation
from api_service import APIService

logger = logging.getLogger(__name__)

class DistanceCalculator:
    """Utility class for distance and cost calculations."""

    @staticmethod
    def calculate_location_distance(loc1: LocationBase, loc2: LocationBase) -> float:
        """
        Calculate Euclidean distance between two locations.

        Args:
            loc1 (LocationBase): First location.
            loc2 (LocationBase): Second location.

        Returns:
            float: Distance.
        """
        lat_diff = loc2.latitude - loc1.latitude
        lon_diff = loc2.longitude - loc1.longitude
        return math.sqrt(lat_diff ** 2 + lon_diff ** 2)

    @staticmethod
    def calculate_cost(central: LocationBase, source: LocationBase, dest: LocationBase) -> float:
        """
        Compute cost based on distance from source to dest relative to central.

        Args:
            central (LocationBase): Central location.
            source (LocationBase): Source location.
            dest (LocationBase): Destination location.

        Returns:
            float: Cost.
        """
        dist_help = DistanceCalculator.calculate_location_distance(source, dest)
        dist_center = DistanceCalculator.calculate_location_distance(central, source)
        return dist_help - dist_center


class EmergencySolver:
    """Class for solving emergency dispatch logic."""

    def __init__(self, api_service: APIService):
        self.api_service = api_service
        self.resource_fields = ["medical", "fire", "police", "rescue", "utility"]

    def find_locations_epicenter(self, locations: list[Location], county: str) -> list[float]:
        """
        Find the average location (epicenter) for a given county.

        Args:
            locations (list[Location]): All available locations.
            county (str): Target county.

        Returns:
            list[float]: Latitude and longitude of the epicenter.
        """
        lat_sum = lon_sum = count = 0
        for loc in locations:
            if loc.county == county:
                lat_sum += loc.latitude
                lon_sum += loc.longitude
                count += 1
        return [lat_sum / count, lon_sum / count] if count > 0 else [0.0, 0.0]

    def rank_locations_by_distance(self, central: LocationBase, locations: list[Location]) -> list[Location]:
        """
        Rank supply locations based on distance from central.

        Args:
            central (LocationBase): Central location.
            locations (list[Location]): Locations to rank.

        Returns:
            list[Location]: Sorted by proximity.
        """
        distance_list = []
        for loc in locations:
            distance = DistanceCalculator.calculate_location_distance(central, loc)
            total_available = sum(
                self.api_service.get_service_for_city(resource, loc.city, loc.county)
                for resource in self.resource_fields
            )
            if total_available > 0:
                logger.debug(f"Location {loc.city} has total available: {total_available}, distance: {distance}")
                distance_list.append((loc, distance))

        return [loc for loc, _ in sorted(distance_list, key=lambda x: x[1])]

    def rank_external_suppliers(self, central: LocationBase, city_in_need: Location, locations: list[Location]) -> list[Location]:
        """
        Rank external suppliers based on cost.

        Args:
            central (LocationBase): Central point.
            city_in_need (Location): Emergency location.
            locations (list[Location]): Supplier pool.

        Returns:
            list[Location]: Ranked by cost.
        """
        cost_list = [
            (loc, DistanceCalculator.calculate_cost(central, city_in_need, loc))
            for loc in locations
        ]
        return [loc for loc, _ in sorted(cost_list, key=lambda x: x[1])]

    def solve_emergency(self, central: LocationBase, emergency_location: EmergencyLocation, supply_locations: list[Location]) -> tuple[list[int], bool]:
        """
        Solve a given emergency by dispatching resources from the supply pool.

        Args:
            central (LocationBase): Epicenter.
            emergency_location (EmergencyLocation): Emergency.
            supply_locations (list[Location]): All supply locations.

        Returns:
            tuple[list[int], bool]: Indices of removed locations and completion status.
        """
        if emergency_location.county != "Maramureș":
            supply_locations = self.rank_external_suppliers(central, emergency_location, supply_locations)

        return self._fulfill_emergency_needs(emergency_location, supply_locations)

    def _fulfill_emergency_needs(self, emergency: EmergencyLocation, suppliers: list[Location]) -> tuple[list[int], bool]:
        needed = {
            field: getattr(emergency, field)
            for field in self.resource_fields
            if getattr(emergency, field, 0) > 0
        }
        indices_to_remove = []
        logger.info(f"EMERGENCY at {emergency.city}: needs {needed}")

        for i, supplier in enumerate(suppliers):
            availability = {
                field: self.api_service.get_service_for_city(field, supplier.city, supplier.county)
                for field in self.resource_fields
            }

            if all(qty == 0 for qty in availability.values()):
                logger.info(f"Skipping {supplier.city}: no available resources.")
                indices_to_remove.append(i)
                continue

            for resource, amount_needed in needed.items():
                available = availability.get(resource, 0)
                if amount_needed <= 0 or available <= 0:
                    continue

                to_dispatch = min(available, amount_needed)
                logger.info(f"Dispatching {to_dispatch} {resource} from {supplier.city} to {emergency.city}")
                self.api_service.dispatch_service_to_city(
                    resource,
                    supplier.city,
                    supplier.county,
                    emergency.city,
                    emergency.county,
                    to_dispatch,
                )
                needed[resource] -= to_dispatch

            if all(v <= 0 for v in needed.values()):
                return indices_to_remove, True

        if any(v > 0 for v in needed.values()):
            logger.warning(f"Emergency at {emergency.city} could not be fully resolved. Remaining needs: {needed}")
            return indices_to_remove, False

        return indices_to_remove, True
