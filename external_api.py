"""
External API integrations for fetching real places and prices
"""
import requests
import time
from typing import List, Dict, Optional
from geopy.distance import geodesic
from geopy.geocoders import Nominatim


class PlacesAPI:
    """Fetch places from OpenStreetMap and other sources"""
    
    def __init__(self):
        self.geolocator = Nominatim(user_agent="ecotravel-v2.0")
        self.overpass_url = "https://overpass-api.de/api/interpreter"
    
    def find_places_along_route(
        self, 
        start_lat: float, 
        start_lng: float, 
        end_lat: float, 
        end_lng: float,
        categories: List[str] = None,
        max_distance_km: int = 50
    ) -> List[Dict]:
        """
        Find interesting places along the route using OpenStreetMap data
        
        Args:
            start_lat, start_lng: Starting coordinates
            end_lat, end_lng: Ending coordinates
            categories: List of preferred categories
            max_distance_km: Maximum distance from route
            
        Returns:
            List of places with details
        """
        places = []
        
        # Calculate intermediate points along the route
        route_points = self._calculate_route_points(start_lat, start_lng, end_lat, end_lng)
        
        # Fetch places for each point
        for point in route_points:
            point_places = self._fetch_nearby_places(
                point['lat'], 
                point['lng'], 
                radius_km=max_distance_km,
                categories=categories
            )
            places.extend(point_places)
        
        # Remove duplicates and sort by importance
        unique_places = self._deduplicate_places(places)
        
        return unique_places[:15]  # Limit to top 15 places
    
    def _calculate_route_points(
        self, 
        start_lat: float, 
        start_lng: float, 
        end_lat: float, 
        end_lng: float,
        num_points: int = 5
    ) -> List[Dict]:
        """Calculate intermediate points along the route"""
        points = []
        
        for i in range(num_points):
            ratio = i / (num_points - 1) if num_points > 1 else 0
            lat = start_lat + (end_lat - start_lat) * ratio
            lng = start_lng + (end_lng - start_lng) * ratio
            points.append({'lat': lat, 'lng': lng})
        
        return points
    
    def _fetch_nearby_places(
        self,
        lat: float,
        lng: float,
        radius_km: int = 20,
        categories: List[str] = None
    ) -> List[Dict]:
        """
        Fetch nearby places using Overpass API (OpenStreetMap) - GLOBAL SUPPORT
        Supports: Attractions, Hotels, Restaurants, Entertainment, Nature, Culture
        """
        places = []
        
        # Radius in meters
        radius_m = radius_km * 1000
        
        # Comprehensive Overpass QL query for ALL POI types
        query = f"""
        [out:json][timeout:30];
        (
          /* Tourist Attractions */
          node["tourism"="attraction"](around:{radius_m},{lat},{lng});
          way["tourism"="attraction"](around:{radius_m},{lat},{lng});
          node["tourism"="museum"](around:{radius_m},{lat},{lng});
          way["tourism"="museum"](around:{radius_m},{lat},{lng});
          node["tourism"="viewpoint"](around:{radius_m},{lat},{lng});
          node["tourism"="gallery"](around:{radius_m},{lat},{lng});
          node["tourism"="artwork"](around:{radius_m},{lat},{lng});
          node["tourism"="theme_park"](around:{radius_m},{lat},{lng});
          way["tourism"="theme_park"](around:{radius_m},{lat},{lng});
          node["tourism"="zoo"](around:{radius_m},{lat},{lng});
          way["tourism"="zoo"](around:{radius_m},{lat},{lng});
          
          /* Accommodation */
          node["tourism"="hotel"](around:{radius_m},{lat},{lng});
          way["tourism"="hotel"](around:{radius_m},{lat},{lng});
          node["tourism"="hostel"](around:{radius_m},{lat},{lng});
          node["tourism"="guest_house"](around:{radius_m},{lat},{lng});
          node["tourism"="motel"](around:{radius_m},{lat},{lng});
          node["tourism"="apartment"](around:{radius_m},{lat},{lng});
          
          /* Restaurants & Food */
          node["amenity"="restaurant"](around:{radius_m},{lat},{lng});
          node["amenity"="cafe"](around:{radius_m},{lat},{lng});
          node["amenity"="fast_food"](around:{radius_m},{lat},{lng});
          node["amenity"="bar"](around:{radius_m},{lat},{lng});
          node["amenity"="pub"](around:{radius_m},{lat},{lng});
          node["amenity"="food_court"](around:{radius_m},{lat},{lng});
          
          /* Entertainment */
          node["amenity"="cinema"](around:{radius_m},{lat},{lng});
          node["amenity"="theatre"](around:{radius_m},{lat},{lng});
          node["amenity"="nightclub"](around:{radius_m},{lat},{lng});
          node["leisure"="amusement_arcade"](around:{radius_m},{lat},{lng});
          node["leisure"="water_park"](around:{radius_m},{lat},{lng});
          way["leisure"="water_park"](around:{radius_m},{lat},{lng});
          
          /* Nature & Outdoor */
          node["natural"="peak"](around:{radius_m},{lat},{lng});
          node["natural"="volcano"](around:{radius_m},{lat},{lng});
          node["natural"="waterfall"](around:{radius_m},{lat},{lng});
          node["natural"="beach"](around:{radius_m},{lat},{lng});
          way["natural"="beach"](around:{radius_m},{lat},{lng});
          node["natural"="hot_spring"](around:{radius_m},{lat},{lng});
          node["leisure"="park"](around:{radius_m},{lat},{lng});
          way["leisure"="park"](around:{radius_m},{lat},{lng});
          node["leisure"="nature_reserve"](around:{radius_m},{lat},{lng});
          way["leisure"="nature_reserve"](around:{radius_m},{lat},{lng});
          
          /* Historical & Cultural */
          node["historic"](around:{radius_m},{lat},{lng});
          way["historic"](around:{radius_m},{lat},{lng});
          node["historic"="castle"](around:{radius_m},{lat},{lng});
          way["historic"="castle"](around:{radius_m},{lat},{lng});
          node["historic"="monument"](around:{radius_m},{lat},{lng});
          node["historic"="archaeological_site"](around:{radius_m},{lat},{lng});
          way["historic"="archaeological_site"](around:{radius_m},{lat},{lng});
          node["historic"="ruins"](around:{radius_m},{lat},{lng});
          way["historic"="ruins"](around:{radius_m},{lat},{lng});
        );
        out center 100;
        """
        
        try:
            time.sleep(1)  # Rate limiting
            response = requests.post(
                self.overpass_url,
                data={'data': query},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                for element in data.get('elements', []):
                    place = self._parse_osm_element(element, lat, lng)
                    if place:
                        places.append(place)
            
        except Exception as e:
            print(f"Error fetching places: {e}")
        
        return places
    
    def _parse_osm_element(self, element: Dict, ref_lat: float, ref_lng: float) -> Optional[Dict]:
        """Parse OSM element into our place format"""
        try:
            # Get coordinates
            if 'lat' in element and 'lon' in element:
                lat, lng = element['lat'], element['lon']
            elif 'center' in element:
                lat, lng = element['center']['lat'], element['center']['lon']
            else:
                return None
            
            tags = element.get('tags', {})
            name = tags.get('name', tags.get('name:en', 'Unknown Place'))
            
            # Skip unnamed places
            if name == 'Unknown Place':
                return None
            
            # Determine category
            category = self._determine_category(tags)
            
            # Get description
            description = tags.get('description', tags.get('tourism', category))
            
            # Calculate distance from reference point
            distance = geodesic((ref_lat, ref_lng), (lat, lng)).km
            
            # Estimate costs (placeholder - would need real API)
            cost_basic = self._estimate_cost(tags, 'basic')
            cost_mid = self._estimate_cost(tags, 'mid')
            cost_luxury = self._estimate_cost(tags, 'luxury')
            
            # Estimate visit duration
            visit_duration = self._estimate_duration(tags)
            
            # Rating (placeholder - would need reviews API)
            rating = 4.0
            
            return {
                'name': name,
                'location': {'lat': lat, 'lng': lng},
                'category': category,
                'description': description,
                'visit_duration': visit_duration,
                'cost_basic': cost_basic,
                'cost_mid': cost_mid,
                'cost_luxury': cost_luxury,
                'rating': rating,
                'distance_from_route': distance,
                'source': 'osm',
                'osm_id': element.get('id'),
                'city': self._get_city_name(lat, lng)
            }
        
        except Exception as e:
            print(f"Error parsing element: {e}")
            return None
    
    def _determine_category(self, tags: Dict) -> str:
        """Determine detailed category from OSM tags"""
        # Accommodation
        if tags.get('tourism') in ['hotel', 'hostel', 'guest_house', 'motel', 'apartment']:
            return 'accommodation'
        
        # Food & Drink
        if tags.get('amenity') in ['restaurant', 'cafe', 'fast_food', 'bar', 'pub', 'food_court']:
            return 'gastronomy'
        
        # Entertainment
        if tags.get('amenity') in ['cinema', 'theatre', 'nightclub']:
            return 'entertainment'
        if tags.get('leisure') in ['amusement_arcade', 'water_park']:
            return 'entertainment'
        
        # Culture & History
        if tags.get('tourism') in ['museum', 'gallery', 'artwork']:
            return 'culture'
        if tags.get('historic'):
            return 'culture'
        
        # Nature & Outdoor
        if tags.get('natural') in ['peak', 'volcano', 'waterfall', 'beach', 'hot_spring']:
            return 'nature'
        if tags.get('leisure') in ['park', 'nature_reserve']:
            return 'nature'
        if tags.get('tourism') in ['viewpoint']:
            return 'nature'
        
        # Theme parks & Attractions
        if tags.get('tourism') in ['attraction', 'theme_park', 'zoo']:
            return 'attraction'
        
        return 'attraction'
    
    def _estimate_cost(self, tags: Dict, tier: str) -> float:
        """Estimate visit/service cost based on tags and tier - GLOBAL PRICING"""
        tourism_type = tags.get('tourism', 'default')
        amenity_type = tags.get('amenity', 'default')
        
        # Base costs in Turkish Lira (2026 estimates)
        base_costs = {
            'basic': {
                'museum': 150, 'attraction': 200, 'viewpoint': 0, 'theme_park': 800,
                'hotel': 600, 'hostel': 300, 'guest_house': 400,
                'restaurant': 250, 'cafe': 100, 'fast_food': 120, 'bar': 150,
                'cinema': 200, 'theatre': 350, 'nightclub': 300,
                'default': 100
            },
            'mid': {
                'museum': 350, 'attraction': 450, 'viewpoint': 50, 'theme_park': 1500,
                'hotel': 1500, 'hostel': 600, 'guest_house': 800,
                'restaurant': 600, 'cafe': 250, 'fast_food': 200, 'bar': 300,
                'cinema': 350, 'theatre': 650, 'nightclub': 600,
                'default': 300
            },
            'luxury': {
                'museum': 700, 'attraction': 900, 'viewpoint': 200, 'theme_park': 3000,
                'hotel': 4500, 'hostel': 1200, 'guest_house': 1800,
                'restaurant': 1500, 'cafe': 600, 'fast_food': 400, 'bar': 800,
                'cinema': 600, 'theatre': 1200, 'nightclub': 1500,
                'default': 800
            }
        }
        
        tier_costs = base_costs.get(tier, base_costs['basic'])
        
        # Try tourism type first
        if tourism_type != 'default' and tourism_type in tier_costs:
            return tier_costs[tourism_type]
        
        # Try amenity type
        if amenity_type != 'default' and amenity_type in tier_costs:
            return tier_costs[amenity_type]
        
        # Natural attractions are usually free or very cheap
        if tags.get('natural'):
            return tier_costs.get('viewpoint', 0)
        
        return tier_costs['default']
    
    def _estimate_duration(self, tags: Dict) -> int:
        """Estimate visit/stay duration in hours"""
        tourism_type = tags.get('tourism', 'attraction')
        amenity_type = tags.get('amenity', '')
        
        # Accommodation - duration in nights (will be converted to hours: 24h)
        if tourism_type in ['hotel', 'hostel', 'guest_house', 'motel']:
            return 24  # 1 night = 24 hours (for calculation purposes)
        
        # Attractions & Culture
        durations = {
            'museum': 3,
            'castle': 2,
            'viewpoint': 1,
            'attraction': 2,
            'monument': 1,
            'archaeological_site': 3,
            'theme_park': 6,
            'zoo': 4,
            'gallery': 2,
            'artwork': 1,
        }
        
        # Entertainment
        entertainment_durations = {
            'cinema': 2,
            'theatre': 3,
            'nightclub': 4,
        }
        
        # Food & Drink
        food_durations = {
            'restaurant': 2,
            'cafe': 1,
            'fast_food': 1,
            'bar': 2,
            'pub': 2,
        }
        
        # Check all duration maps
        if tourism_type in durations:
            return durations[tourism_type]
        if amenity_type in entertainment_durations:
            return entertainment_durations[amenity_type]
        if amenity_type in food_durations:
            return food_durations[amenity_type]
        
        # Natural sites - usually longer visits
        if tags.get('natural'):
            return 3
        
        return 2  # Default
    
    def _get_city_name(self, lat: float, lng: float) -> str:
        """Get city name from coordinates"""
        try:
            time.sleep(1)  # Rate limiting
            location = self.geolocator.reverse(f"{lat}, {lng}", language='tr', timeout=10)
            
            if location and location.raw.get('address'):
                address = location.raw['address']
                return (
                    address.get('city') or 
                    address.get('town') or 
                    address.get('village') or 
                    address.get('county') or 
                    'Bilinmeyen Şehir'
                )
        except Exception:
            pass
        
        return 'Bilinmeyen Şehir'
    
    def _deduplicate_places(self, places: List[Dict]) -> List[Dict]:
        """Remove duplicate places based on proximity and name similarity"""
        if not places:
            return []
        
        unique_places = []
        seen_names = set()
        
        for place in places:
            name_lower = place['name'].lower()
            
            # Check if similar name already exists
            is_duplicate = False
            for seen_name in seen_names:
                if self._similar_strings(name_lower, seen_name):
                    # Check if they're close together (within 1km)
                    for existing in unique_places:
                        if existing['name'].lower() == seen_name:
                            dist = geodesic(
                                (place['location']['lat'], place['location']['lng']),
                                (existing['location']['lat'], existing['location']['lng'])
                            ).km
                            if dist < 1:  # Within 1km
                                is_duplicate = True
                                break
                    if is_duplicate:
                        break
            
            if not is_duplicate:
                unique_places.append(place)
                seen_names.add(name_lower)
        
        # Sort by rating and distance
        unique_places.sort(key=lambda x: (-x['rating'], x['distance_from_route']))
        
        return unique_places
    
    def _similar_strings(self, s1: str, s2: str) -> bool:
        """Check if two strings are similar (simple approach)"""
        # Simple similarity: check if one contains the other
        return s1 in s2 or s2 in s1 or s1[:5] == s2[:5]


class AccommodationAPI:
    """Fetch accommodation prices (placeholder for real API)"""
    
    def get_accommodation_prices(self, city: str, date: str) -> Dict:
        """
        Get accommodation prices for a city
        Would integrate with Booking.com, Airbnb APIs
        """
        # Placeholder: return estimated prices based on city
        base_prices = {
            'basic': 400,
            'mid': 1200,
            'luxury': 3500
        }
        
        # Apply city multiplier (big cities more expensive)
        multiplier = 1.0
        expensive_cities = ['istanbul', 'ankara', 'izmir', 'antalya']
        
        if any(city_name in city.lower() for city_name in expensive_cities):
            multiplier = 1.5
        
        return {
            'basic': {'name': 'Hostel/Pansiyon', 'cost_per_night': base_prices['basic'] * multiplier},
            'mid': {'name': '3 Yıldız Otel', 'cost_per_night': base_prices['mid'] * multiplier},
            'luxury': {'name': '5 Yıldız Otel', 'cost_per_night': base_prices['luxury'] * multiplier}
        }


class TransportAPI:
    """Fetch transportation prices (placeholder for real API)"""
    
    def get_transport_prices(self, start: str, end: str, date: str) -> Dict:
        """
        Get transportation prices between two locations
        Would integrate with bus/flight APIs
        """
        # Placeholder implementation
        return {
            'basic': {'type': 'Otobüs', 'price': 500},
            'mid': {'type': 'Uçak (Ekonomi)', 'price': 1200},
            'luxury': {'type': 'Uçak (Business)', 'price': 3500}
        }
