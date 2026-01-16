# ?? EcoTravel - Global Features Documentation

## Overview
EcoTravel now supports **worldwide travel planning** with comprehensive POI (Points of Interest) discovery using OpenStreetMap's global database.

---

## ?? Global Location Support

### Geocoding
- **Worldwide coverage**: Any city, country, address, or landmark
- **Examples**: 
  - "Paris, France"
  - "New York City"
  - "Eiffel Tower"
  - "Tokyo, Japan"
  - "Sydney Opera House"

### How It Works
1. User enters location name (any language, any country)
2. System uses **Nominatim (OpenStreetMap)** for geocoding
3. Returns coordinates (latitude, longitude)
4. System finds nearby POIs using **Overpass API**

### API Endpoint
```
POST /api/geocode
Body: {"location": "Paris, France"}
Response: {
  "success": true,
  "location": {
    "lat": 48.8566,
    "lng": 2.3522,
    "display_name": "Paris, Île-de-France, France"
  }
}
```

---

## ?? Comprehensive POI Categories

### ??? Attractions
OpenStreetMap Tags:
- `tourism=attraction`
- `tourism=museum`
- `tourism=gallery`
- `tourism=viewpoint`
- `tourism=theme_park`
- `tourism=zoo`
- `tourism=artwork`

**Examples Worldwide:**
- Eiffel Tower (Paris)
- Statue of Liberty (New York)
- Colosseum (Rome)
- Taj Mahal (India)
- Great Wall (China)

### ?? Accommodation
OpenStreetMap Tags:
- `tourism=hotel`
- `tourism=hostel`
- `tourism=guest_house`
- `tourism=motel`
- `tourism=apartment`

**Pricing Tiers:**
- Basic: 300-600 TRY/night equivalent
- Mid: 1500-2000 TRY/night equivalent
- Luxury: 4500+ TRY/night equivalent

### ??? Gastronomy (Food & Drink)
OpenStreetMap Tags:
- `amenity=restaurant`
- `amenity=cafe`
- `amenity=fast_food`
- `amenity=bar`
- `amenity=pub`
- `amenity=food_court`

**Meal Cost Estimates:**
- Basic: 120-250 TRY/meal
- Mid: 200-600 TRY/meal
- Luxury: 600-1500 TRY/meal

### ?? Entertainment
OpenStreetMap Tags:
- `amenity=cinema`
- `amenity=theatre`
- `amenity=nightclub`
- `leisure=amusement_arcade`
- `leisure=water_park`

**Activity Costs:**
- Cinema: 200-600 TRY
- Theatre: 350-1200 TRY
- Nightclub: 300-1500 TRY

### ?? Nature & Outdoor
OpenStreetMap Tags:
- `natural=peak` (mountains)
- `natural=volcano`
- `natural=waterfall`
- `natural=beach`
- `natural=hot_spring`
- `leisure=park`
- `leisure=nature_reserve`

**Usually FREE or very cheap** (0-200 TRY)

### ??? History & Culture
OpenStreetMap Tags:
- `historic=castle`
- `historic=monument`
- `historic=archaeological_site`
- `historic=ruins`
- `historic=memorial`

**Entry Fees:**
- Basic: 150-450 TRY
- Mid: 350-700 TRY
- Luxury: 700-1200 TRY (with guided tours)

---

## ??? Dynamic Route Planning

### Route Point Calculation
The system calculates **intermediate points** along your route:
- Start ? 25% ? 50% ? 75% ? End
- Each point searches for POIs within configurable radius (default: 50km)

### Example Route
**Paris ? Lyon (France)**
- Start: Paris (48.8566, 2.3522)
- Point 1 (25%): Near Fontainebleau
- Point 2 (50%): Near Auxerre
- Point 3 (75%): Near Mâcon
- End: Lyon (45.7640, 4.8357)

System finds POIs near each point ? deduplicates ? sorts by rating & distance

---

## ?? API: Get POIs by Category

### Endpoint
```
POST /api/pois-by-category
```

### Request Body
```json
{
  "start_lat": 48.8566,
  "start_lng": 2.3522,
  "end_lat": 45.7640,
  "end_lng": 4.8357,
  "radius_km": 50
}
```

### Response
```json
{
  "success": true,
  "pois": {
    "attractions": [
      {
        "name": "Eiffel Tower",
        "location": {"lat": 48.8584, "lng": 2.2945},
        "category": "attraction",
        "description": "Iconic iron tower in Paris",
        "visit_duration": 3,
        "cost_basic": 800,
        "cost_mid": 1500,
        "cost_luxury": 3000,
        "rating": 4.8,
        "distance_from_route": 2.5,
        "source": "osm",
        "city": "Paris"
      }
    ],
    "accommodation": [...],
    "gastronomy": [...],
    "entertainment": [...],
    "nature": [...],
    "culture": [...]
  },
  "counts": {
    "attractions": 15,
    "accommodation": 8,
    "gastronomy": 12,
    "entertainment": 5,
    "nature": 7,
    "culture": 10
  },
  "total": 57
}
```

---

## ?? Global Demo Scenarios

### Included Scenarios

1. **?? Paris Tour (5 days)**
   - Round trip in Paris
   - Budget: 30,000 TRY
   - Categories: Culture, Gastronomy

2. **?? New York ? Washington DC (7 days)**
   - US East Coast tour
   - Budget: 45,000 TRY
   - Categories: Culture, Gastronomy

3. **?? Tokyo Tour (6 days)**
   - Round trip in Tokyo
   - Budget: 40,000 TRY
   - Categories: Culture, Gastronomy

4. **?? Rome ? Venice (5 days)**
   - Italian art & culture tour
   - Budget: 35,000 TRY
   - Categories: Culture, Gastronomy

---

## ?? Technical Details

### External API: OpenStreetMap Overpass
- **Base URL**: `https://overpass-api.de/api/interpreter`
- **Query Language**: Overpass QL
- **Rate Limiting**: 1 second delay between requests
- **Timeout**: 30 seconds per query
- **Max Results**: 100 elements per query

### Geocoding: Nominatim
- **Base URL**: Built into geopy
- **User Agent**: `EcoTravel-Global/2.0`
- **Language**: English (configurable)
- **Timeout**: 10 seconds

### Cost Estimation Algorithm
```python
def estimate_cost(tags, tier):
    # Base costs for each POI type
    # Adjusts based on:
    # - Tourism type (museum, hotel, restaurant)
    # - Amenity type (cinema, bar)
    # - Natural features (usually free)
    # - Tier multiplier (basic=1x, mid=2-3x, luxury=5-8x)
```

---

## ?? Usage Examples

### Example 1: Paris Tour
```javascript
const request = {
  start_location: "Paris, France",
  start_lat: 48.8566,
  start_lng: 2.3522,
  end_location: "",  // Round trip
  days: 5,
  budget: 30000,
  preferences: ["culture", "gastronomy"]
};
```

**Result**: 
- Eiffel Tower, Louvre Museum, Arc de Triomphe
- French restaurants, cafes
- Hotels in different tiers
- Estimated costs for each tier

### Example 2: London ? Edinburgh
```javascript
const request = {
  start_location: "London, UK",
  start_lat: 51.5074,
  start_lng: -0.1278,
  end_location: "Edinburgh, Scotland",
  end_lat: 55.9533,
  end_lng: -3.1883,
  days: 7,
  budget: 40000,
  preferences: ["culture", "nature"]
};
```

**Result**:
- POIs in London: Big Ben, British Museum
- POIs along route: York Minster, Durham Cathedral
- POIs in Edinburgh: Edinburgh Castle, Arthur's Seat
- Accommodation options in each city

---

## ?? Data Sources

### Primary Source: OpenStreetMap
- **Contributors**: 8+ million worldwide
- **POIs**: 1+ billion points of interest
- **Updates**: Real-time (community-driven)
- **Coverage**: Entire world
- **License**: Open Database License (ODbL)

### Local Database (Fallback)
- **Coverage**: Turkey (40+ cities)
- **POIs**: 26 curated locations
- **Purpose**: Faster lookup for Turkish cities
- **Updates**: Manual (maintained by EcoTravel)

---

## ?? Privacy & Performance

### Rate Limiting
- Overpass API: 1 request/second
- Nominatim: 1 request/second
- User requests: No limit (cached results recommended)

### Caching Strategy (Recommended)
```python
# Cache geocoding results for 24 hours
# Cache POI results for 6 hours
# Reduces API calls by 80-90%
```

### Privacy
- No user data stored
- No tracking cookies
- API calls anonymous
- Geolocation opt-in (GPS button)

---

## ?? Troubleshooting

### Issue: "Location not found"
**Solution**: 
- Use more specific location (city + country)
- Use English spelling
- Try landmark instead of address

### Issue: "No POIs found"
**Solution**:
- Increase radius (default 50km ? 100km)
- Check if location is remote area
- Try nearby major city

### Issue: "API timeout"
**Solution**:
- Reduce search radius
- Limit to 2-3 categories
- Retry after 1 minute

---

## ?? Future Enhancements

### Planned Features
- [ ] Real-time pricing from booking APIs
- [ ] User reviews integration (TripAdvisor API)
- [ ] Weather forecasts
- [ ] Flight/train booking integration
- [ ] Multi-language support (UI)
- [ ] Mobile app (React Native)
- [ ] Offline mode (cached maps)

---

## ?? Support

For questions or issues:
- GitHub Issues: [https://github.com/yunusdemir2009/EcoTravel/issues](https://github.com/yunusdemir2009/EcoTravel/issues)
- Documentation: `README.md`, `API.md`, `DEVELOPMENT.md`

---

**Last Updated**: 2025-01-XX  
**Version**: 2.0 (Global Edition)  
**Author**: EcoTravel Team
