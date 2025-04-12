import logging
from models import LocationBase, EmergencyLocation
from api_service import APIService
from utils import EmergencySolver

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class AlgorithmEngine:
    """
    Manages simulation state, including location ranking and emergency resolution.
    """

    def __init__(self):
        self.api_service = APIService()
        self.solver = EmergencySolver(self.api_service)
        self.locations = []
        self.ranking = []

    def run(self):
        """Run the main algorithm loop for emergency handling."""
        self.api_service.start_simulation()
        self.api_service.authenticate()
        self.locations = self.api_service.get_locations()

        epicenter_coords = self.solver.find_locations_epicenter(self.locations, "Maramureș")
        epicenter = LocationBase(
            county="Maramureș",
            city="Epicenter",
            latitude=epicenter_coords[0],
            longitude=epicenter_coords[1],
        )

        self.ranking = self.solver.rank_locations_by_distance(epicenter, self.locations)
        emergency = self.api_service.next()

        while emergency is not None:
            emergency_obj = self._parse_emergency(emergency)
            indices_to_remove, completed = self.solver.solve_emergency(epicenter, emergency_obj, self.ranking)
            logger.info(f"Emergency in {emergency_obj.city} completed: {completed}")

            for i in sorted(indices_to_remove, reverse=True):
                del self.ranking[i]

            emergency = self.api_service.next()

        response = self.api_service.stop_simulation()
        logger.info(f"Simulation ended. Response: {response}")

    def _parse_emergency(self, payload: dict) -> EmergencyLocation:
        """
        Parse raw emergency payload into EmergencyLocation instance.

        Args:
            payload (dict): Raw payload.

        Returns:
            EmergencyLocation: Parsed object.
        """
        type_mapping = {
            "Medical": "medical",
            "Fire": "fire",
            "Police": "police",
            "Rescue": "rescue",
            "Utility": "utility",
        }

        city = payload.get("city", "")
        county = payload.get("county", "")
        latitude = payload.get("latitude", 0.0)
        longitude = payload.get("longitude", 0.0)
        resource_data = {field: 0 for field in type_mapping.values()}

        for req in payload.get("requests", []):
            key = type_mapping.get(req.get("Type"))
            if key:
                resource_data[key] = req.get("Quantity", 0)

        return EmergencyLocation(
            county=county,
            city=city,
            latitude=latitude,
            longitude=longitude,
            **resource_data,
        )


if __name__ == "__main__":
    AlgorithmEngine().run()
