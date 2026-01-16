"""
Service layer for EcoTravel application.
Separates business logic from route handlers.
"""
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from typing import Dict, List, Optional, Tuple
import time

from data import TURKISH_CITIES, POI_DATABASE, ACCOMMODATION_DATABASE
from exceptions import ResourceNotFoundError, ValidationError
from external_api import PlacesAPI, AccommodationAPI, TransportAPI


class GeocodeService:
    """Service for geocoding and reverse geocoding"""

    def __init__(self):
        self.geolocator = Nominatim(user_agent="ecotravel-app-v1.0")
        self.cities_db = TURKISH_CITIES

    def geocode(self, location_name: str) -> Optional[Dict]:
        """
        Convert location name to coordinates
        
        Args:
            location_name: Name of the location
            
        Returns:
            Dictionary with lat, lng, and name, or None if not found
        """
        # First, check local database
        location_key = location_name.lower().strip()
        if location_key in self.cities_db:
            city_data = self.cities_db[location_key]
            return {
                "lat": city_data["lat"],
                "lng": city_data["lng"],
                "location_name": city_data["name"],
            }

        # Try geopy geocoding
        try:
            time.sleep(1)  # Rate limiting for Nominatim
            location = self.geolocator.geocode(location_name + ", Turkey", timeout=10)
            if location:
                return {
                    "lat": location.latitude,
                    "lng": location.longitude,
                    "location_name": location.address,
                }
        except Exception:
            pass

        return None

    def reverse_geocode(self, lat: float, lng: float) -> str:
        """
        Convert coordinates to location name
        
        Args:
            lat: Latitude
            lng: Longitude
            
        Returns:
            Location name string
        """
        # First check if close to any known city
        for city_data in self.cities_db.values():
            dist = geodesic((lat, lng), (city_data["lat"], city_data["lng"])).km
            if dist < 10:  # Within 10km
                return city_data["name"]

        # Try reverse geocoding with geopy
        try:
            time.sleep(1)  # Rate limiting
            location = self.geolocator.reverse(f"{lat}, {lng}", timeout=10)
            if location and location.address:
                return location.address
        except Exception:
            pass

        # Fallback to coordinates
        return f"Lat: {lat:.4f}, Lng: {lng:.4f}"


class POIService:
    """Service for managing Points of Interest"""

    def __init__(self):
        self.pois = POI_DATABASE

    def get_pois(self, category: Optional[str] = None, city: Optional[str] = None) -> List[Dict]:
        """
        Get POIs with optional filtering
        
        Args:
            category: Filter by category
            city: Filter by city
            
        Returns:
            List of POI dictionaries
        """
        filtered = self.pois

        if category:
            filtered = [poi for poi in filtered if poi["category"] == category]

        if city:
            filtered = [poi for poi in filtered if poi["city"].lower() == city.lower()]

        return filtered

    def get_poi_by_id(self, poi_id: int) -> Optional[Dict]:
        """Get a single POI by ID"""
        for poi in self.pois:
            if poi["id"] == poi_id:
                return poi
        return None

    def __init__(self, pois_db: List[Dict] = None):
        self.pois = pois_db or POI_DATABASE
        self.places_api = PlacesAPI()  # For fetching real places

    def find_pois_near_route(
        self, start_loc: Dict, end_loc: Dict, preferences: List[str], max_pois: int = 5, search_radius_km: int = 100, use_external: bool = True
    ) -> List[Dict]:
        """
        Find POIs near a route - uses both local database and external APIs
        
        Args:
            start_loc: Starting location with lat/lng
            end_loc: Ending location with lat/lng
            preferences: List of preferred categories
            max_pois: Maximum number of POIs to return
            search_radius_km: Search radius in kilometers
            use_external: Whether to fetch from external sources (OSM)
            
        Returns:
            List of nearby POIs sorted by rating
        """
        pois = []

        # Check if round trip
        is_round_trip = (
            abs(start_loc["lat"] - end_loc["lat"]) < 0.01 and abs(start_loc["lng"] - end_loc["lng"]) < 0.01
        )

        # Larger radius for round trips
        radius = search_radius_km * 3 if is_round_trip else search_radius_km

        # First, check local database
        for poi in self.pois:
            # Filter by category
            if preferences and poi["category"] not in preferences:
                continue

            # Check distance to start or end
            dist_to_start = self._calculate_distance(start_loc, poi["location"])
            dist_to_end = self._calculate_distance(end_loc, poi["location"])

            if dist_to_start < radius or dist_to_end < radius:
                poi_copy = poi.copy()
                poi_copy["distance_to_start"] = dist_to_start
                poi_copy["distance_to_end"] = dist_to_end
                pois.append(poi_copy)

        # If external API is enabled and we don't have enough POIs, fetch from OpenStreetMap
        if use_external and len(pois) < max_pois:
            try:
                external_places = self.places_api.find_places_along_route(
                    start_loc["lat"],
                    start_loc["lng"],
                    end_loc["lat"],
                    end_loc["lng"],
                    categories=preferences,
                    max_distance_km=radius
                )
                
                # Add external places to our list
                for place in external_places:
                    # Convert to our format
                    poi_data = {
                        "name": place["name"],
                        "location": place["location"],
                        "category": place["category"],
                        "description": place["description"],
                        "visit_duration": place["visit_duration"],
                        "cost": {
                            "basic": place["cost_basic"],
                            "mid": place["cost_mid"],
                            "luxury": place["cost_luxury"]
                        },
                        "rating": place["rating"],
                        "city": place["city"],
                        "distance_to_start": place["distance_from_route"],
                        "distance_to_end": place["distance_from_route"],
                        "source": "osm"  # Mark as external
                    }
                    pois.append(poi_data)
            except Exception as e:
                print(f"Error fetching external places: {e}")

        # Sort by rating and limit
        pois.sort(key=lambda x: x["rating"], reverse=True)
        return pois[:max_pois]

    @staticmethod
    def _calculate_distance(loc1: Dict, loc2: Dict) -> float:
        """Calculate distance between two locations in km"""
        return geodesic((loc1["lat"], loc1["lng"]), (loc2["lat"], loc2["lng"])).km


class AccommodationService:
    """Service for accommodation recommendations"""

    def __init__(self):
        self.accommodations = ACCOMMODATION_DATABASE

    def get_accommodation(self, city: str, tier: str) -> Optional[Dict]:
        """
        Get accommodation for a city and tier
        
        Args:
            city: City name
            tier: Accommodation tier (basic, mid, luxury)
            
        Returns:
            Accommodation dictionary or None
        """
        for acc in self.accommodations:
            if acc["city"].lower() == city.lower():
                return acc.get(tier)
        return None

    def calculate_accommodation_cost(self, city: str, nights: int, tier: str) -> Tuple[Dict, float]:
        """
        Calculate accommodation cost
        
        Returns:
            Tuple of (accommodation_info, total_cost)
        """
        accommodation = self.get_accommodation(city, tier)
        if not accommodation:
            # Default accommodation if city not found
            default_costs = {"basic": 400, "mid": 1200, "luxury": 3500}
            accommodation = {"name": "Standart Konaklama", "cost_per_night": default_costs.get(tier, 1000)}

        total_cost = accommodation["cost_per_night"] * nights
        return accommodation, total_cost


class TransportService:
    """Service for transportation calculations"""

    @staticmethod
    def calculate_distance(loc1: Dict, loc2: Dict) -> float:
        """Calculate distance between two locations in km"""
        # Validate coordinates
        if not (-90 <= loc1["lat"] <= 90) or not (-90 <= loc2["lat"] <= 90):
            raise ValidationError("Geçersiz enlem değeri")
        if not (-180 <= loc1["lng"] <= 180) or not (-180 <= loc2["lng"] <= 180):
            raise ValidationError("Geçersiz boylam değeri")

        return geodesic((loc1["lat"], loc1["lng"]), (loc2["lat"], loc2["lng"])).km

    @staticmethod
    def calculate_transport_cost(distance_km: float, tier: str) -> float:
        """
        Calculate transportation cost based on distance and tier
        
        2026 Türkiye ulaşım maliyetleri
        """
        if distance_km < 5:  # City transport
            base_cost = {"basic": 50, "mid": 150, "luxury": 400}
            return base_cost.get(tier, 100)
        elif distance_km < 50:  # Suburban
            cost_per_km = {"basic": 5.0, "mid": 10.0, "luxury": 25.0}
            return distance_km * cost_per_km.get(tier, 8.0)
        else:  # Intercity
            cost_per_km = {"basic": 8.0, "mid": 15.0, "luxury": 35.0}
            return distance_km * cost_per_km.get(tier, 12.0)

    @staticmethod
    def calculate_food_cost(days: int, tier: str) -> float:
        """Calculate daily food cost based on tier"""
        cost_per_day = {
            "basic": 800,  # Local restaurants
            "mid": 1500,  # Mid-range restaurants
            "luxury": 3500,  # Fine dining
        }
        return days * cost_per_day.get(tier, 1200)


class TravelPlannerService:
    """Main service for creating travel plans"""

    def __init__(self):
        self.poi_service = POIService()
        self.accommodation_service = AccommodationService()
        self.transport_service = TransportService()

    def create_travel_plans(
        self,
        start_location: str,
        start_lat: float,
        start_lng: float,
        end_location: Optional[str],
        end_lat: Optional[float],
        end_lng: Optional[float],
        days: int,
        budget: float,
        preferences: List[str],
    ) -> Dict:
        """
        Create travel plans for all tiers
        
        Returns:
            Dictionary with basic, mid, and luxury plans
        """
        # Setup locations
        start_loc = {"lat": start_lat, "lng": start_lng, "name": start_location}

        if end_location and end_lat and end_lng:
            end_loc = {"lat": end_lat, "lng": end_lng, "name": end_location}
            is_round_trip = False
        else:
            # Round trip - end at start
            end_loc = start_loc.copy()
            is_round_trip = True

        # Create plans for each tier
        plans = {}
        for tier in ["basic", "mid", "luxury"]:
            plan = self._create_single_plan(start_loc, end_loc, days, budget, preferences, tier, is_round_trip)
            plans[tier] = plan

        return plans

    def _create_single_plan(
        self, start_loc: Dict, end_loc: Dict, days: int, budget: float, preferences: List[str], tier: str, is_round_trip: bool
    ) -> Dict:
        """Create a single travel plan for a specific tier"""
        # Find POIs
        pois = self.poi_service.find_pois_near_route(start_loc, end_loc, preferences, max_pois=min(days * 2, 10))

        # Calculate base transportation
        route_distance = self.transport_service.calculate_distance(start_loc, end_loc)
        if not is_round_trip:
            route_distance *= 2  # Round trip transport

        base_transport_cost = self.transport_service.calculate_transport_cost(route_distance, tier)

        # Calculate food cost
        food_cost = self.transport_service.calculate_food_cost(days, tier)

        # Build itinerary
        daily_itinerary = []
        total_poi_cost = 0
        total_accommodation_cost = 0
        visited_pois = []

        for day in range(1, days + 1):
            day_plan = {"day": day, "activities": [], "accommodation": None, "daily_cost": 0}

            # Add POIs for the day (1-2 per day)
            pois_per_day = min(2, len(pois))
            for _ in range(pois_per_day):
                if pois:
                    poi = pois.pop(0)
                    cost_key = f"cost_{tier}"
                    poi_cost = poi.get(cost_key, 0)

                    day_plan["activities"].append(
                        {
                            "name": poi["name"],
                            "description": poi["description"],
                            "duration": poi["visit_duration"],
                            "cost": poi_cost,
                            "category": poi["category"],
                            "location": poi["location"],
                        }
                    )
                    total_poi_cost += poi_cost
                    visited_pois.append(poi)

            # Add accommodation (except last day)
            if day < days:
                city = start_loc["name"].split(",")[0]  # Extract city name
                accommodation, acc_cost = self.accommodation_service.calculate_accommodation_cost(city, 1, tier)
                day_plan["accommodation"] = accommodation
                day_plan["accommodation"]["cost"] = acc_cost
                total_accommodation_cost += acc_cost

            # Calculate daily cost
            day_cost = sum(a["cost"] for a in day_plan["activities"])
            if day_plan["accommodation"]:
                day_cost += day_plan["accommodation"]["cost"]
            day_plan["daily_cost"] = day_cost

            daily_itinerary.append(day_plan)

        # Calculate totals
        total_cost = base_transport_cost + food_cost + total_poi_cost + total_accommodation_cost
        buffer = total_cost * 0.15  # 15% buffer
        estimated_total = total_cost + buffer

        # Build response
        plan = {
            "tier": tier,
            "is_round_trip": is_round_trip,
            "route": {"start": start_loc, "end": end_loc, "distance_km": route_distance / 2 if not is_round_trip else route_distance},
            "daily_itinerary": daily_itinerary,
            "cost_breakdown": {
                "transportation": base_transport_cost,
                "accommodation": total_accommodation_cost,
                "food": food_cost,
                "activities": total_poi_cost,
                "buffer": buffer,
                "total": estimated_total,
            },
            "budget_status": {"budget": budget, "estimated": estimated_total, "within_budget": estimated_total <= budget, "difference": budget - estimated_total},
        }

        return plan
