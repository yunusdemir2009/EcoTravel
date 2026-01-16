from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
from datetime import datetime, timedelta
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import os

# Import external API functionality
try:
    from external_api import PlacesAPI
    USE_EXTERNAL_API = True
except ImportError:
    USE_EXTERNAL_API = False
    print("Warning: external_api module not available, using local database only")

app = Flask(__name__)
CORS(app)

# Initialize geocoder and places API
geolocator = Nominatim(user_agent="ecotravel-dynamic-v1.0")
places_api = PlacesAPI() if USE_EXTERNAL_API else None

# Configuration constants
DEFAULT_CITY = "Ankara"
POI_SEARCH_RADIUS_KM = 100  # Maximum distance to search for POIs

# Turkish cities database for geocoding fallback
TURKISH_CITIES = {
    "ankara": {"lat": 39.9334, "lng": 32.8597, "name": "Ankara"},
    "çankaya": {"lat": 39.9181, "lng": 32.8619, "name": "Çankaya, Ankara"},
    "kızılay": {"lat": 39.9191, "lng": 32.8543, "name": "Kızılay, Ankara"},
    "istanbul": {"lat": 41.0082, "lng": 28.9784, "name": "İstanbul"},
    "İstanbul": {"lat": 41.0082, "lng": 28.9784, "name": "İstanbul"},  # Capital İ support
    "beyoğlu": {"lat": 41.0370, "lng": 28.9784, "name": "Beyoğlu, İstanbul"},
    "kadıköy": {"lat": 40.9833, "lng": 29.0333, "name": "Kadıköy, İstanbul"},
    "beşiktaş": {"lat": 41.0428, "lng": 29.0078, "name": "Beşiktaş, İstanbul"},
    "izmir": {"lat": 38.4237, "lng": 27.1428, "name": "İzmir"},
    "İzmir": {"lat": 38.4237, "lng": 27.1428, "name": "İzmir"},  # Capital İ support
    "konak": {"lat": 38.4189, "lng": 27.1287, "name": "Konak, İzmir"},
    "karşıyaka": {"lat": 38.4597, "lng": 27.1142, "name": "Karşıyaka, İzmir"},
    "antalya": {"lat": 36.8969, "lng": 30.7133, "name": "Antalya"},
    "muratpaşa": {"lat": 36.8889, "lng": 30.7061, "name": "Muratpaşa, Antalya"},
    "bursa": {"lat": 40.1826, "lng": 29.0665, "name": "Bursa"},
    "osmangazi": {"lat": 40.1873, "lng": 29.0591, "name": "Osmangazi, Bursa"},
    "adana": {"lat": 37.0000, "lng": 35.3213, "name": "Adana"},
    "seyhan": {"lat": 37.0011, "lng": 35.3160, "name": "Seyhan, Adana"},
    "gaziantep": {"lat": 37.0662, "lng": 37.3833, "name": "Gaziantep"},
    "şehitkamil": {"lat": 37.0662, "lng": 37.3833, "name": "Şehitkamil, Gaziantep"},
    "konya": {"lat": 37.8746, "lng": 32.4932, "name": "Konya"},
    "meram": {"lat": 37.8706, "lng": 32.4858, "name": "Meram, Konya"},
    "kayseri": {"lat": 38.7312, "lng": 35.4787, "name": "Kayseri"},
    "melikgazi": {"lat": 38.7205, "lng": 35.4897, "name": "Melikgazi, Kayseri"},
    "eskişehir": {"lat": 39.7767, "lng": 30.5206, "name": "Eskişehir"},
    "odunpazarı": {"lat": 39.7833, "lng": 30.5333, "name": "Odunpazarı, Eskişehir"},
    "trabzon": {"lat": 41.0027, "lng": 39.7168, "name": "Trabzon"},
    "ortahisar": {"lat": 40.9939, "lng": 39.7217, "name": "Ortahisar, Trabzon"},
    "denizli": {"lat": 37.7765, "lng": 29.0864, "name": "Denizli"},
    "pamukkale": {"lat": 37.9200, "lng": 29.1200, "name": "Pamukkale, Denizli"},
    "nevşehir": {"lat": 38.6431, "lng": 34.8286, "name": "Nevşehir"},
    "kapadokya": {"lat": 38.6431, "lng": 34.8286, "name": "Kapadokya, Nevşehir"},
    "fethiye": {"lat": 36.6542, "lng": 29.1256, "name": "Fethiye"},
    "ölüdeniz": {"lat": 36.5500, "lng": 29.1167, "name": "Ölüdeniz, Fethiye"},
    "adıyaman": {"lat": 37.7648, "lng": 38.2786, "name": "Adıyaman"},
    "nemrut": {"lat": 37.9803, "lng": 38.7414, "name": "Nemrut, Adıyaman"},
}

# Sample POI data (Points of Interest) - 2026 fiyatlarıyla
POI_DATABASE = [
    # Ankara
    {"id": 1, "name": "Anıtkabir", "location": {"lat": 39.9250, "lng": 32.8369}, "city": "Ankara", "category": "culture",
     "description": "Atatürk'ün anıt mezarı ve müzesi", "visit_duration": 2, "cost_basic": 0, "cost_mid": 100, "cost_luxury": 250, "rating": 4.9},
    {"id": 2, "name": "Ankara Kalesi", "location": {"lat": 39.9392, "lng": 32.8647}, "city": "Ankara", "category": "culture",
     "description": "Tarihi kale ve panoramik şehir manzarası", "visit_duration": 2, "cost_basic": 0, "cost_mid": 50, "cost_luxury": 150, "rating": 4.5},
    {"id": 3, "name": "Anadolu Medeniyetleri Müzesi", "location": {"lat": 39.9402, "lng": 32.8625}, "city": "Ankara", "category": "culture",
     "description": "Anadolu'nun tarihi ve arkeolojik eserleri", "visit_duration": 3, "cost_basic": 150, "cost_mid": 200, "cost_luxury": 350, "rating": 4.7},
    
    # Kapadokya Bölgesi
    {"id": 4, "name": "Kapadokya Sıcak Hava Balonu", "location": {"lat": 38.6431, "lng": 34.8286}, "city": "Nevşehir", "category": "nature",
     "description": "Eşsiz manzarada sıcak hava balonu turu", "visit_duration": 3, "cost_basic": 3500, "cost_mid": 5000, "cost_luxury": 8000, "rating": 4.9},
    {"id": 5, "name": "Göreme Açık Hava Müzesi", "location": {"lat": 38.6425, "lng": 34.8284}, "city": "Nevşehir", "category": "culture",
     "description": "Kayaya oyulmuş kiliseler ve freskleri", "visit_duration": 3, "cost_basic": 450, "cost_mid": 600, "cost_luxury": 900, "rating": 4.8},
    {"id": 6, "name": "Derinkuyu Yeraltı Şehri", "location": {"lat": 38.3738, "lng": 34.7342}, "city": "Nevşehir", "category": "culture",
     "description": "8 katlı antik yeraltı şehri", "visit_duration": 2, "cost_basic": 350, "cost_mid": 450, "cost_luxury": 700, "rating": 4.6},
    
    # İstanbul
    {"id": 7, "name": "Topkapı Sarayı", "location": {"lat": 41.0115, "lng": 28.9833}, "city": "İstanbul", "category": "culture",
     "description": "Osmanlı İmparatorluğu'nun muhteşem sarayı", "visit_duration": 3, "cost_basic": 500, "cost_mid": 800, "cost_luxury": 1500, "rating": 4.8},
    {"id": 8, "name": "Ayasofya Camii", "location": {"lat": 41.0086, "lng": 28.9802}, "city": "İstanbul", "category": "culture",
     "description": "1500 yıllık tarihi yapı", "visit_duration": 2, "cost_basic": 0, "cost_mid": 150, "cost_luxury": 400, "rating": 4.9},
    {"id": 9, "name": "Boğaz Turu", "location": {"lat": 41.0400, "lng": 29.0050}, "city": "İstanbul", "category": "nature",
     "description": "İstanbul Boğazı'nda tekne turu", "visit_duration": 3, "cost_basic": 400, "cost_mid": 800, "cost_luxury": 2000, "rating": 4.7},
    {"id": 10, "name": "Kapalıçarşı", "location": {"lat": 41.0106, "lng": 28.9680}, "city": "İstanbul", "category": "gastronomy",
     "description": "Tarihi kapalı çarşı ve alışveriş", "visit_duration": 3, "cost_basic": 200, "cost_mid": 500, "cost_luxury": 1500, "rating": 4.5},
    {"id": 11, "name": "Dolmabahçe Sarayı", "location": {"lat": 41.0391, "lng": 29.0003}, "city": "İstanbul", "category": "culture",
     "description": "Boğaz kıyısındaki görkemli saray", "visit_duration": 2, "cost_basic": 400, "cost_mid": 600, "cost_luxury": 1000, "rating": 4.7},
    
    # İzmir ve Çevresi
    {"id": 12, "name": "Efes Antik Kenti", "location": {"lat": 37.9392, "lng": 27.3409}, "city": "İzmir", "category": "culture",
     "description": "Dünyanın en iyi korunmuş antik Roma şehri", "visit_duration": 4, "cost_basic": 450, "cost_mid": 700, "cost_luxury": 1200, "rating": 4.9},
    {"id": 13, "name": "Şirince Köyü", "location": {"lat": 37.9478, "lng": 27.4497}, "city": "İzmir", "category": "gastronomy",
     "description": "Şarap ve geleneksel lezzetler", "visit_duration": 3, "cost_basic": 300, "cost_mid": 600, "cost_luxury": 1200, "rating": 4.6},
    {"id": 14, "name": "Alaçatı", "location": {"lat": 38.2667, "lng": 26.3667}, "city": "İzmir", "category": "nature",
     "description": "Rüzgar sörfü ve taş evler", "visit_duration": 5, "cost_basic": 500, "cost_mid": 1000, "cost_luxury": 2500, "rating": 4.7},
    
    # Antalya
    {"id": 15, "name": "Kaleiçi", "location": {"lat": 36.8854, "lng": 30.7056}, "city": "Antalya", "category": "culture",
     "description": "Tarihi liman ve dar sokaklar", "visit_duration": 3, "cost_basic": 0, "cost_mid": 200, "cost_luxury": 600, "rating": 4.6},
    {"id": 16, "name": "Düden Şelalesi", "location": {"lat": 36.9108, "lng": 30.7614}, "city": "Antalya", "category": "nature",
     "description": "Muhteşem doğal şelale", "visit_duration": 2, "cost_basic": 150, "cost_mid": 250, "cost_luxury": 500, "rating": 4.5},
    {"id": 17, "name": "Perge Antik Kenti", "location": {"lat": 36.9614, "lng": 30.8522}, "city": "Antalya", "category": "culture",
     "description": "Roma dönemi antik kent", "visit_duration": 3, "cost_basic": 300, "cost_mid": 450, "cost_luxury": 800, "rating": 4.4},
    
    # Pamukkale
    {"id": 18, "name": "Pamukkale Travertenleri", "location": {"lat": 37.9200, "lng": 29.1200}, "city": "Denizli", "category": "nature",
     "description": "Beyaz travertenler ve termal havuzlar", "visit_duration": 4, "cost_basic": 400, "cost_mid": 700, "cost_luxury": 1400, "rating": 4.8},
    {"id": 19, "name": "Hierapolis Antik Kenti", "location": {"lat": 37.9244, "lng": 29.1258}, "city": "Denizli", "category": "culture",
     "description": "Pamukkale üzerindeki antik şehir", "visit_duration": 2, "cost_basic": 200, "cost_mid": 350, "cost_luxury": 650, "rating": 4.6},
    
    # Fethiye
    {"id": 20, "name": "Ölüdeniz Plajı", "location": {"lat": 36.5500, "lng": 29.1167}, "city": "Fethiye", "category": "nature",
     "description": "Turkuaz lagün ve muhteşem plaj", "visit_duration": 6, "cost_basic": 300, "cost_mid": 700, "cost_luxury": 1800, "rating": 4.9},
    {"id": 21, "name": "Yamaç Paraşütü (Ölüdeniz)", "location": {"lat": 36.5485, "lng": 29.1103}, "city": "Fethiye", "category": "nature",
     "description": "Babadağ'dan yamaç paraşütü deneyimi", "visit_duration": 3, "cost_basic": 1500, "cost_mid": 2000, "cost_luxury": 3500, "rating": 4.9},
    {"id": 22, "name": "Saklıkent Kanyonu", "location": {"lat": 36.4833, "lng": 29.3167}, "city": "Fethiye", "category": "nature",
     "description": "18 km uzunluğunda dev kanyon", "visit_duration": 4, "cost_basic": 250, "cost_mid": 450, "cost_luxury": 900, "rating": 4.7},
    
    # Konya
    {"id": 23, "name": "Mevlana Müzesi", "location": {"lat": 37.8712, "lng": 32.5044}, "city": "Konya", "category": "culture",
     "description": "Mevlana'nın türbesi ve müzesi", "visit_duration": 2, "cost_basic": 0, "cost_mid": 100, "cost_luxury": 300, "rating": 4.7},
    
    # Adıyaman
    {"id": 24, "name": "Nemrut Dağı", "location": {"lat": 37.9803, "lng": 38.7414}, "city": "Adıyaman", "category": "nature",
     "description": "Dev heykeller ve büyüleyici gün doğumu", "visit_duration": 6, "cost_basic": 600, "cost_mid": 1000, "cost_luxury": 2000, "rating": 4.8},
    
    # Bursa
    {"id": 25, "name": "Uludağ", "location": {"lat": 40.0969, "lng": 29.2706}, "city": "Bursa", "category": "nature",
     "description": "Kayak merkezi ve teleferik", "visit_duration": 6, "cost_basic": 800, "cost_mid": 1500, "cost_luxury": 3500, "rating": 4.6},
    {"id": 26, "name": "Bursa Ulu Cami", "location": {"lat": 40.1833, "lng": 29.0625}, "city": "Bursa", "category": "culture",
     "description": "Osmanlı mimarisinin şaheseri", "visit_duration": 1, "cost_basic": 0, "cost_mid": 50, "cost_luxury": 150, "rating": 4.5}
]

# Konaklama veritabanı - 2026 gerçekçi fiyatlar
ACCOMMODATION_DATABASE = [
    {"city": "Ankara", "basic": {"name": "Hostel/Pansiyon", "cost_per_night": 400}, "mid": {"name": "3 Yıldız Otel", "cost_per_night": 1200}, "luxury": {"name": "5 Yıldız Otel", "cost_per_night": 3500}},
    {"city": "Nevşehir", "basic": {"name": "Pansiyon", "cost_per_night": 600}, "mid": {"name": "Mağara Otel", "cost_per_night": 1800}, "luxury": {"name": "Butik Mağara Otel", "cost_per_night": 5000}},
    {"city": "İzmir", "basic": {"name": "Hostel", "cost_per_night": 450}, "mid": {"name": "3 Yıldız Otel", "cost_per_night": 1400}, "luxury": {"name": "5 Yıldız Sahil Oteli", "cost_per_night": 4500}},
    {"city": "Denizli", "basic": {"name": "Pansiyon", "cost_per_night": 500}, "mid": {"name": "Termal Otel", "cost_per_night": 1500}, "luxury": {"name": "Termal Spa Resort", "cost_per_night": 4000}},
    {"city": "İstanbul", "basic": {"name": "Hostel", "cost_per_night": 600}, "mid": {"name": "Butik Otel", "cost_per_night": 2200}, "luxury": {"name": "5 Yıldız Boğaz Oteli", "cost_per_night": 7000}},
    {"city": "Fethiye", "basic": {"name": "Pansiyon", "cost_per_night": 550}, "mid": {"name": "Resort Otel", "cost_per_night": 1800}, "luxury": {"name": "Luxury Beach Resort", "cost_per_night": 5500}},
    {"city": "Antalya", "basic": {"name": "Pansiyon", "cost_per_night": 550}, "mid": {"name": "4 Yıldız Otel", "cost_per_night": 1900}, "luxury": {"name": "5 Yıldız Ultra Her Şey Dahil", "cost_per_night": 6000}},
    {"city": "Adıyaman", "basic": {"name": "Otel", "cost_per_night": 400}, "mid": {"name": "3 Yıldız Otel", "cost_per_night": 1000}, "luxury": {"name": "Dağ Evi Resort", "cost_per_night": 2800}},
    {"city": "Konya", "basic": {"name": "Otel", "cost_per_night": 400}, "mid": {"name": "3 Yıldız Otel", "cost_per_night": 1100}, "luxury": {"name": "Lüks Otel", "cost_per_night": 3000}},
    {"city": "Bursa", "basic": {"name": "Pansiyon", "cost_per_night": 450}, "mid": {"name": "3 Yıldız Otel", "cost_per_night": 1300}, "luxury": {"name": "Termal Resort", "cost_per_night": 4000}}
]

def calculate_distance(loc1, loc2):
    """Calculate distance between two locations in km"""
    # Validate coordinates
    if not (-90 <= loc1["lat"] <= 90) or not (-90 <= loc2["lat"] <= 90):
        raise ValueError("Latitude must be between -90 and 90")
    if not (-180 <= loc1["lng"] <= 180) or not (-180 <= loc2["lng"] <= 180):
        raise ValueError("Longitude must be between -180 and 180")
    
    return geodesic((loc1["lat"], loc1["lng"]), (loc2["lat"], loc2["lng"])).km

def calculate_transport_cost(distance_km, tier):
    """Calculate transportation cost based on distance and tier"""
    # 2026 Türkiye gerçek ulaşım maliyetleri
    if distance_km < 5:  # Şehir içi (taksi/toplu taşıma)
        base_cost = {"basic": 50, "mid": 150, "luxury": 400}
        return base_cost.get(tier, 100)
    elif distance_km < 50:  # Şehir çevresi
        cost_per_km = {"basic": 5.0, "mid": 10.0, "luxury": 25.0}
        return distance_km * cost_per_km.get(tier, 8.0)
    else:  # Şehirlerarası
        cost_per_km = {"basic": 8.0, "mid": 15.0, "luxury": 35.0}
        return distance_km * cost_per_km.get(tier, 12.0)

def calculate_food_cost(days, tier):
    """Calculate food cost per day based on tier"""
    # 2026 günlük yemek maliyetleri (kahvaltı, öğle, akşam)
    cost_per_day = {
        "basic": 800,    # Esnaf lokantası, sokak lezzetleri
        "mid": 1500,     # Orta segment restoranlar
        "luxury": 3500   # Fine dining, özel menüler
    }
    return days * cost_per_day.get(tier, 1200)

def find_pois_near_route(start_loc, end_loc, preferences, max_pois=5):
    """Find POIs near the route - now supports external API for any location"""
    pois = []
    
    # Determine if it's a round trip (same start and end)
    is_round_trip = (
        abs(start_loc["lat"] - end_loc["lat"]) < 0.01 and 
        abs(start_loc["lng"] - end_loc["lng"]) < 0.01
    )
    
    # Use larger radius for round trips to get more variety
    search_radius = POI_SEARCH_RADIUS_KM * 3 if is_round_trip else POI_SEARCH_RADIUS_KM
    
    # First, check local database
    for poi in POI_DATABASE:
        # Filter by category if specified
        if preferences is not None and len(preferences) > 0:
            if poi["category"] not in preferences:
                continue
            
        # Calculate if POI is reasonably close to start or end
        dist_to_start = calculate_distance(start_loc, poi["location"])
        dist_to_end = calculate_distance(end_loc, poi["location"])
        
        if dist_to_start < search_radius or dist_to_end < search_radius:
            poi_copy = poi.copy()
            poi_copy["distance_from_start"] = round(dist_to_start, 2)
            pois.append(poi_copy)
    
    # If we don't have enough POIs from local database and external API is available,
    # fetch from OpenStreetMap
    if len(pois) < max_pois and USE_EXTERNAL_API and places_api:
        try:
            print(f"Fetching external places for route ({start_loc['lat']},{start_loc['lng']}) to ({end_loc['lat']},{end_loc['lng']})")
            external_places = places_api.find_places_along_route(
                start_loc["lat"],
                start_loc["lng"],
                end_loc["lat"],
                end_loc["lng"],
                categories=preferences,
                max_distance_km=search_radius
            )
            
            print(f"Found {len(external_places)} external places")
            
            # Convert external places to our POI format
            for place in external_places:
                poi_data = {
                    "id": f"osm_{place.get('osm_id', hash(place['name']))}",
                    "name": place["name"],
                    "location": place["location"],
                    "city": place["city"],
                    "category": place["category"],
                    "description": place["description"],
                    "visit_duration": place["visit_duration"],
                    "cost_basic": place["cost_basic"],
                    "cost_mid": place["cost_mid"],
                    "cost_luxury": place["cost_luxury"],
                    "rating": place["rating"],
                    "distance_from_start": round(place["distance_from_route"], 2),
                    "source": "osm"
                }
                pois.append(poi_data)
        except Exception as e:
            print(f"Error fetching external places: {e}")
    
    # Sort by rating and distance
    pois.sort(key=lambda x: (-x["rating"], x["distance_from_start"]))
    return pois[:max_pois]

def get_accommodation_for_city(city, tier):
    """Get accommodation information for a city"""
    for acc in ACCOMMODATION_DATABASE:
        if acc["city"] == city:
            return acc.get(tier, acc.get("mid"))
    # Default accommodation
    default_costs = {"basic": 500, "mid": 1500, "luxury": 4000}
    return {"name": "Otel", "cost_per_night": default_costs.get(tier, 1200)}

def create_itinerary(start_loc, end_loc, days, budget, tier, preferences):
    """Create a day-by-day itinerary"""
    itinerary = []
    
    # Find POIs along the route
    pois = find_pois_near_route(start_loc, end_loc, preferences)
    
    # Distribute POIs across days
    pois_per_day = max(1, len(pois) // days)
    
    total_cost = 0
    current_location = start_loc.copy()
    
    for day in range(1, days + 1):
        day_plan = {
            "day": day,
            "date": (datetime.now() + timedelta(days=day-1)).strftime("%Y-%m-%d"),
            "activities": [],
            "accommodation": None,
            "daily_cost": 0
        }
        
        # Add POIs for this day
        start_idx = (day - 1) * pois_per_day
        end_idx = min(start_idx + pois_per_day, len(pois))
        day_pois = pois[start_idx:end_idx]
        
        for poi in day_pois:
            # Calculate transport to POI
            distance = calculate_distance(current_location, poi["location"])
            transport_cost = calculate_transport_cost(distance, tier)
            
            # Get POI cost based on tier - handle both formats
            if f"cost_{tier}" in poi:
                poi_cost = poi[f"cost_{tier}"]
            elif "cost" in poi and isinstance(poi["cost"], dict):
                poi_cost = poi["cost"].get(tier, poi["cost"].get("mid", 0))
            else:
                poi_cost = 0
            
            activity = {
                "name": poi["name"],
                "description": poi["description"],
                "duration": poi["visit_duration"],
                "cost": poi_cost + transport_cost,
                "category": poi["category"],
                "location": poi["location"]
            }
            
            day_plan["activities"].append(activity)
            day_plan["daily_cost"] += activity["cost"]
            current_location = poi["location"]
        
        # Add accommodation (except last day if returning home)
        if day < days or current_location != start_loc:
            # Find nearest city for accommodation
            nearest_city = DEFAULT_CITY
            if day_pois:
                nearest_city = day_pois[-1]["city"]
            
            accommodation = get_accommodation_for_city(nearest_city, tier)
            day_plan["accommodation"] = accommodation
            day_plan["daily_cost"] += accommodation["cost_per_night"]
        
        # Add food cost
        food_cost = calculate_food_cost(1, tier)
        day_plan["daily_cost"] += food_cost
        day_plan["food_cost"] = food_cost
        
        total_cost += day_plan["daily_cost"]
        itinerary.append(day_plan)
    
    return itinerary, total_cost

def generate_travel_plan(start_loc, end_loc, days, budget, preferences):
    """Generate travel plans for all three tiers"""
    plans = {}
    
    for tier in ["basic", "mid", "luxury"]:
        itinerary, total_cost = create_itinerary(
            start_loc, end_loc, days, budget, tier, preferences
        )
        
        # Calculate cost range (min-max)
        min_cost = total_cost * 0.9  # 10% lower
        max_cost = total_cost * 1.1  # 10% higher
        
        plans[tier] = {
            "tier": tier,
            "tier_name": {
                "basic": "Ekonomik Plan",
                "mid": "Orta Seviye Plan",
                "luxury": "Lüks Plan"
            }[tier],
            "total_days": days,
            "estimated_cost": round(total_cost, 2),
            "min_cost": round(min_cost, 2),
            "max_cost": round(max_cost, 2),
            "itinerary": itinerary,
            "fits_budget": total_cost <= budget
        }
    
    return plans

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/plan', methods=['POST'])
def create_plan():
    """Create a travel plan based on user input"""
    try:
        data = request.json
        
        # Extract user inputs
        start_location_name = data.get('start_location', 'Ankara')
        start_lat = data.get('start_lat')
        start_lng = data.get('start_lng')
        
        end_location_name = data.get('end_location')
        end_lat = data.get('end_lat')
        end_lng = data.get('end_lng')
        
        days = int(data.get('days', 5))
        budget = float(data.get('budget', 5000))
        preferences = data.get('preferences', [])  # ['nature', 'culture', 'gastronomy']
        
        # Build location objects
        if start_lat is None or start_lng is None:
            # Default to Ankara
            start_lat, start_lng = 39.9334, 32.8597
        
        start_location = {
            "lat": float(start_lat),
            "lng": float(start_lng),
            "name": start_location_name
        }
        
        # If no end location, use start location (round trip)
        if end_lat is None or end_lng is None or not end_location_name:
            end_location = start_location
        else:
            end_location = {
                "lat": float(end_lat),
                "lng": float(end_lng),
                "name": end_location_name
            }
        
        # Generate plans for all tiers
        plans = generate_travel_plan(start_location, end_location, days, budget, preferences)
        
        return jsonify({
            "success": True,
            "plans": plans
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

@app.route('/api/pois', methods=['GET'])
def get_pois():
    """Get all available POIs"""
    return jsonify({
        "success": True,
        "pois": POI_DATABASE
    })

@app.route('/api/review', methods=['POST'])
def submit_review():
    """Submit a review for a POI"""
    try:
        data = request.json
        poi_id = data.get('poi_id')
        rating = data.get('rating')
        comment = data.get('comment')
        
        # In a real app, this would save to a database
        return jsonify({
            "success": True,
            "message": "Yorum başarıyla gönderildi"
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

@app.route('/api/geocode', methods=['POST'])
def geocode():
    """Geocode a location name to coordinates"""
    try:
        data = request.json
        location_name = data.get('location')
        
        if not location_name:
            return jsonify({
                "success": False,
                "error": "Location name is required"
            }), 400
        
        # Normalize location name for lookup
        normalized_name = location_name.lower().strip()
        # Remove "turkey", "türkiye" from the search
        normalized_name = normalized_name.replace(", turkey", "").replace(", türkiye", "")
        
        # Try to find in our Turkish cities database first
        for key, value in TURKISH_CITIES.items():
            if key in normalized_name or normalized_name in key:
                return jsonify({
                    "success": True,
                    "location": {
                        "lat": value["lat"],
                        "lng": value["lng"],
                        "display_name": value["name"]
                    }
                })
        
        # Fallback: Try geopy if available (might not work in restricted environments)
        try:
            from geopy.geocoders import Nominatim
            geolocator = Nominatim(user_agent="EcoTravel/1.0", timeout=5)
            
            # Add Turkey to improve results
            query = f"{location_name}, Turkey"
            location = geolocator.geocode(query)
            
            if location:
                return jsonify({
                    "success": True,
                    "location": {
                        "lat": location.latitude,
                        "lng": location.longitude,
                        "display_name": location.address
                    }
                })
        except Exception as geo_error:
            print(f"Geopy geocoding failed: {geo_error}")
        
        # If nothing found, return error
        return jsonify({
            "success": False,
            "error": f"'{location_name}' için konum bulunamadı. Lütfen il veya ilçe adını deneyin (örn: İstanbul, Ankara, Antalya)"
        }), 404
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

@app.route('/api/reverse-geocode', methods=['POST'])
def reverse_geocode():
    """Reverse geocode coordinates to location name"""
    try:
        data = request.json
        lat = data.get('lat')
        lng = data.get('lng')
        
        if lat is None or lng is None:
            return jsonify({
                "success": False,
                "error": "Latitude and longitude are required"
            }), 400
        
        # Try to find closest city in our database
        min_distance = float('inf')
        closest_city = None
        
        # Use geodesic distance for more accurate calculation
        from geopy.distance import geodesic
        
        for city_data in TURKISH_CITIES.values():
            distance_km = geodesic((lat, lng), (city_data["lat"], city_data["lng"])).km
            if distance_km < min_distance:
                min_distance = distance_km
                closest_city = city_data
        
        # If within reasonable distance (50km)
        MAX_CITY_DISTANCE_KM = 50  # Maximum distance to consider city as match
        if closest_city and min_distance < MAX_CITY_DISTANCE_KM:
            return jsonify({
                "success": True,
                "location_name": closest_city["name"]
            })
        
        # Fallback: Try geopy if available
        try:
            from geopy.geocoders import Nominatim
            geolocator = Nominatim(user_agent="EcoTravel/1.0", timeout=5)
            
            location = geolocator.reverse((lat, lng))
            
            if location and location.raw.get('address'):
                address = location.raw['address']
                parts = []
                
                # Build location name from address parts
                if address.get('suburb') or address.get('neighbourhood'):
                    parts.append(address.get('suburb') or address.get('neighbourhood'))
                if address.get('city') or address.get('town'):
                    parts.append(address.get('city') or address.get('town'))
                if address.get('province') or address.get('state'):
                    parts.append(address.get('province') or address.get('state'))
                
                location_name = ', '.join(parts) if parts else location.address
                
                return jsonify({
                    "success": True,
                    "location_name": location_name
                })
        except Exception as geo_error:
            print(f"Geopy reverse geocoding failed: {geo_error}")
        
        # Default: return coordinates
        return jsonify({
            "success": True,
            "location_name": f"Lat: {lat:.4f}, Lng: {lng:.4f}"
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

if __name__ == '__main__':
    # Debug mode should only be enabled in development
    # In production, use a proper WSGI server like gunicorn
    import os
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
