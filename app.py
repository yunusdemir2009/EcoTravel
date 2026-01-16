from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
from datetime import datetime, timedelta
from geopy.distance import geodesic
import os

app = Flask(__name__)
CORS(app)

# Configuration constants
DEFAULT_CITY = "Ankara"
POI_SEARCH_RADIUS_KM = 500  # Maximum distance to search for POIs

# Turkish cities database for geocoding fallback
TURKISH_CITIES = {
    "ankara": {"lat": 39.9334, "lng": 32.8597, "name": "Ankara"},
    "çankaya": {"lat": 39.9181, "lng": 32.8619, "name": "Çankaya, Ankara"},
    "kızılay": {"lat": 39.9191, "lng": 32.8543, "name": "Kızılay, Ankara"},
    "istanbul": {"lat": 41.0082, "lng": 28.9784, "name": "İstanbul"},
    "beyoğlu": {"lat": 41.0370, "lng": 28.9784, "name": "Beyoğlu, İstanbul"},
    "kadıköy": {"lat": 40.9833, "lng": 29.0333, "name": "Kadıköy, İstanbul"},
    "beşiktaş": {"lat": 41.0428, "lng": 29.0078, "name": "Beşiktaş, İstanbul"},
    "izmir": {"lat": 38.4237, "lng": 27.1428, "name": "İzmir"},
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

# Sample POI data (Points of Interest)
POI_DATABASE = [
    {
        "id": 1,
        "name": "Anıtkabir",
        "location": {"lat": 39.9250, "lng": 32.8369},
        "city": "Ankara",
        "category": "culture",
        "description": "Atatürk'ün anıt mezarı",
        "visit_duration": 2,  # hours
        "cost_basic": 0,
        "cost_mid": 50,
        "cost_luxury": 150,
        "rating": 4.8
    },
    {
        "id": 2,
        "name": "Kapadokya",
        "location": {"lat": 38.6431, "lng": 34.8286},
        "city": "Nevşehir",
        "category": "nature",
        "description": "Eşsiz doğal oluşumlar ve sıcak hava balonu",
        "visit_duration": 8,
        "cost_basic": 200,
        "cost_mid": 500,
        "cost_luxury": 1500,
        "rating": 4.9
    },
    {
        "id": 3,
        "name": "Efes Antik Kenti",
        "location": {"lat": 37.9392, "lng": 27.3409},
        "city": "İzmir",
        "category": "culture",
        "description": "Antik Roma şehri kalıntıları",
        "visit_duration": 3,
        "cost_basic": 100,
        "cost_mid": 250,
        "cost_luxury": 500,
        "rating": 4.7
    },
    {
        "id": 4,
        "name": "Pamukkale",
        "location": {"lat": 37.9200, "lng": 29.1200},
        "city": "Denizli",
        "category": "nature",
        "description": "Beyaz travertenler ve termal sular",
        "visit_duration": 4,
        "cost_basic": 150,
        "cost_mid": 300,
        "cost_luxury": 700,
        "rating": 4.6
    },
    {
        "id": 5,
        "name": "Topkapı Sarayı",
        "location": {"lat": 41.0115, "lng": 28.9833},
        "city": "İstanbul",
        "category": "culture",
        "description": "Osmanlı İmparatorluğu'nun sarayı",
        "visit_duration": 3,
        "cost_basic": 200,
        "cost_mid": 400,
        "cost_luxury": 800,
        "rating": 4.7
    },
    {
        "id": 6,
        "name": "Ayasofya",
        "location": {"lat": 41.0086, "lng": 28.9802},
        "city": "İstanbul",
        "category": "culture",
        "description": "Tarihi cami ve müze",
        "visit_duration": 2,
        "cost_basic": 0,
        "cost_mid": 100,
        "cost_luxury": 300,
        "rating": 4.8
    },
    {
        "id": 7,
        "name": "Ölüdeniz",
        "location": {"lat": 36.5500, "lng": 29.1167},
        "city": "Fethiye",
        "category": "nature",
        "description": "Turkuaz rengi plaj ve yamaç paraşütü",
        "visit_duration": 6,
        "cost_basic": 100,
        "cost_mid": 350,
        "cost_luxury": 900,
        "rating": 4.8
    },
    {
        "id": 8,
        "name": "Nemrut Dağı",
        "location": {"lat": 37.9803, "lng": 38.7414},
        "city": "Adıyaman",
        "category": "nature",
        "description": "Dev heykeller ve gün doğumu",
        "visit_duration": 5,
        "cost_basic": 150,
        "cost_mid": 350,
        "cost_luxury": 750,
        "rating": 4.5
    }
]

# Sample accommodation data
ACCOMMODATION_DATABASE = [
    {
        "city": "Ankara",
        "basic": {"name": "Hostel", "cost_per_night": 150},
        "mid": {"name": "3 Yıldız Otel", "cost_per_night": 400},
        "luxury": {"name": "5 Yıldız Otel", "cost_per_night": 1200}
    },
    {
        "city": "Nevşehir",
        "basic": {"name": "Pansiyon", "cost_per_night": 200},
        "mid": {"name": "Mağara Otel", "cost_per_night": 600},
        "luxury": {"name": "Butik Mağara Otel", "cost_per_night": 1500}
    },
    {
        "city": "İzmir",
        "basic": {"name": "Hostel", "cost_per_night": 150},
        "mid": {"name": "3 Yıldız Otel", "cost_per_night": 450},
        "luxury": {"name": "5 Yıldız Sahil Oteli", "cost_per_night": 1400}
    },
    {
        "city": "Denizli",
        "basic": {"name": "Pansiyon", "cost_per_night": 150},
        "mid": {"name": "Termal Otel", "cost_per_night": 500},
        "luxury": {"name": "Termal Spa Resort", "cost_per_night": 1300}
    },
    {
        "city": "İstanbul",
        "basic": {"name": "Hostel", "cost_per_night": 200},
        "mid": {"name": "Butik Otel", "cost_per_night": 700},
        "luxury": {"name": "5 Yıldız Boğaz Oteli", "cost_per_night": 2000}
    },
    {
        "city": "Fethiye",
        "basic": {"name": "Pansiyon", "cost_per_night": 180},
        "mid": {"name": "Resort Otel", "cost_per_night": 550},
        "luxury": {"name": "Luxury Beach Resort", "cost_per_night": 1600}
    },
    {
        "city": "Adıyaman",
        "basic": {"name": "Otel", "cost_per_night": 120},
        "mid": {"name": "3 Yıldız Otel", "cost_per_night": 350},
        "luxury": {"name": "Dağ Evi Resort", "cost_per_night": 900}
    }
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
    # Cost per km by tier (car rental + fuel)
    cost_per_km = {
        "basic": 2.5,  # Bus/shared transport
        "mid": 4.0,    # Rental car economy
        "luxury": 8.0  # Premium car + driver
    }
    return distance_km * cost_per_km.get(tier, 3.0)

def calculate_food_cost(days, tier):
    """Calculate food cost per day based on tier"""
    cost_per_day = {
        "basic": 200,   # Simple meals
        "mid": 400,     # Restaurant meals
        "luxury": 800   # Fine dining
    }
    return days * cost_per_day.get(tier, 300)

def find_pois_near_route(start_loc, end_loc, preferences, max_pois=5):
    """Find POIs near the route"""
    pois = []
    
    for poi in POI_DATABASE:
        # Filter by category if specified
        if preferences is not None and len(preferences) > 0:
            if poi["category"] not in preferences:
                continue
            
        # Calculate if POI is reasonably close to start or end
        dist_to_start = calculate_distance(start_loc, poi["location"])
        dist_to_end = calculate_distance(end_loc, poi["location"])
        
        if dist_to_start < POI_SEARCH_RADIUS_KM or dist_to_end < POI_SEARCH_RADIUS_KM:
            poi_copy = poi.copy()
            poi_copy["distance_from_start"] = round(dist_to_start, 2)
            pois.append(poi_copy)
    
    # Sort by rating and distance
    pois.sort(key=lambda x: (-x["rating"], x["distance_from_start"]))
    return pois[:max_pois]

def get_accommodation_for_city(city, tier):
    """Get accommodation information for a city"""
    for acc in ACCOMMODATION_DATABASE:
        if acc["city"] == city:
            return acc.get(tier, acc.get("mid"))
    # Default accommodation
    default_costs = {"basic": 150, "mid": 400, "luxury": 1000}
    return {"name": "Otel", "cost_per_night": default_costs.get(tier, 300)}

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
            
            # Get POI cost based on tier
            poi_cost = poi.get(f"cost_{tier}", poi.get("cost_mid", 0))
            
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
        start_location = data.get('start_location', {"lat": 39.9334, "lng": 32.8597})  # Default: Ankara
        end_location = data.get('end_location')
        days = int(data.get('days', 5))
        budget = float(data.get('budget', 5000))
        preferences = data.get('preferences', [])  # ['nature', 'culture', 'gastronomy']
        
        # If no end location, use start location (round trip)
        if not end_location:
            end_location = start_location
        
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
        
        for city_data in TURKISH_CITIES.values():
            distance = ((lat - city_data["lat"]) ** 2 + (lng - city_data["lng"]) ** 2) ** 0.5
            if distance < min_distance:
                min_distance = distance
                closest_city = city_data
        
        # If within reasonable distance (about 50km in degrees ~0.5)
        if closest_city and min_distance < 0.5:
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
