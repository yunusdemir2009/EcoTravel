# EcoTravel Geliştirme Kılavuzu

## İçindekiler
1. [Proje Yapısı](#proje-yapısı)
2. [Backend Geliştirme](#backend-geliştirme)
3. [Frontend Geliştirme](#frontend-geliştirme)
4. [Yeni Özellik Ekleme](#yeni-özellik-ekleme)
5. [Test Etme](#test-etme)
6. [Deployment](#deployment)

---

## Proje Yapısı

```
EcoTravel/
├── app.py                      # Flask backend uygulaması (main)
├── requirements.txt            # Python bağımlılıkları
├── .gitignore                 # Git ignore dosyası
├── README.md                  # Proje dokümantasyonu
├── API.md                     # API dokümantasyonu
├── DEVELOPMENT.md             # Geliştirme kılavuzu (bu dosya)
├── test_api.py               # API test script
├── templates/
│   └── index.html            # Ana HTML şablonu
└── static/
    ├── css/
    │   └── style.css         # Ana CSS dosyası
    └── js/
        └── app.js            # Frontend JavaScript

```

---

## Backend Geliştirme

### Flask Uygulama Yapısı

`app.py` dosyası şunları içerir:

1. **Veri Kaynakları**
   - `POI_DATABASE`: Gezilecek yerler listesi
   - `ACCOMMODATION_DATABASE`: Konaklama seçenekleri

2. **Yardımcı Fonksiyonlar**
   - `calculate_distance()`: İki nokta arası mesafe hesaplama
   - `calculate_transport_cost()`: Ulaşım maliyeti hesaplama
   - `calculate_food_cost()`: Yemek maliyeti hesaplama
   - `find_pois_near_route()`: Rota üzerindeki POI'ları bulma
   - `get_accommodation_for_city()`: Şehir için konaklama bulma
   - `create_itinerary()`: Gün gün program oluşturma
   - `generate_travel_plan()`: Üç seviye için plan oluşturma

3. **API Endpoints**
   - `GET /`: Ana sayfa
   - `POST /api/plan`: Gezi planı oluşturma
   - `GET /api/pois`: POI listesi
   - `POST /api/review`: Yorum gönderme

### Yeni POI Ekleme

POI eklemek için `POI_DATABASE` listesine yeni öğe ekleyin:

```python
{
    "id": 9,
    "name": "Yeni Yer",
    "location": {"lat": 0.0, "lng": 0.0},
    "city": "Şehir",
    "category": "nature",  # veya "culture", "gastronomy"
    "description": "Açıklama",
    "visit_duration": 3,  # saat
    "cost_basic": 100,
    "cost_mid": 250,
    "cost_luxury": 500,
    "rating": 4.5
}
```

### Yeni Şehir İçin Konaklama Ekleme

`ACCOMMODATION_DATABASE` listesine yeni öğe ekleyin:

```python
{
    "city": "YeniŞehir",
    "basic": {"name": "Pansiyon", "cost_per_night": 150},
    "mid": {"name": "3 Yıldız Otel", "cost_per_night": 400},
    "luxury": {"name": "5 Yıldız Otel", "cost_per_night": 1200}
}
```

### Yeni API Endpoint Ekleme

```python
@app.route('/api/yeni-endpoint', methods=['POST'])
def yeni_endpoint():
    """Endpoint açıklaması"""
    try:
        data = request.json
        # İşlemler
        return jsonify({
            "success": True,
            "data": result
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
```

---

## Frontend Geliştirme

### HTML Yapısı (`templates/index.html`)

Ana bölümler:
1. Header: Başlık ve slogan
2. Input Section: Kullanıcı girişleri formu
3. Results Section: Plan sonuçları
4. Map Section: Leaflet haritası
5. POI Section: Gezilecek yerler grid
6. Review Modal: Yorum formu

### CSS Stilleri (`static/css/style.css`)

Ana stil kategorileri:
- Global styles ve CSS variables
- Form stilleri
- Button stilleri
- Plan kartları
- Harita stilleri
- POI grid
- Modal stilleri
- Responsive tasarım

### JavaScript (`static/js/app.js`)

Ana fonksiyonlar:
- `handleTravelFormSubmit()`: Form gönderme
- `displayPlans()`: Planları görüntüleme
- `switchPlanTab()`: Plan sekmesi değiştirme
- `displayPlanContent()`: Plan içeriği render
- `updateMap()`: Harita güncelleme
- `loadPOIs()`: POI'ları yükleme
- `openReviewModal()`: Yorum modalı açma

### Yeni UI Component Ekleme

1. HTML'e yeni section ekleyin:
```html
<section class="yeni-section">
    <h2>Başlık</h2>
    <div id="yeniContent"></div>
</section>
```

2. CSS stilleri ekleyin:
```css
.yeni-section {
    padding: 30px;
    background: white;
    border-radius: 10px;
}
```

3. JavaScript fonksiyonu ekleyin:
```javascript
function loadYeniContent() {
    const container = document.getElementById('yeniContent');
    // İçerik oluştur
    container.innerHTML = html;
}
```

---

## Yeni Özellik Ekleme

### Örnek: Hava Durumu Entegrasyonu

1. **Backend'e API ekleyin:**

```python
import requests

def get_weather(city):
    """Hava durumu bilgisi al"""
    # API key kullanarak hava durumu çek
    api_key = os.getenv('WEATHER_API_KEY')
    url = f"https://api.weatherapi.com/v1/current.json?key={api_key}&q={city}"
    response = requests.get(url)
    return response.json()

@app.route('/api/weather/<city>', methods=['GET'])
def weather(city):
    """Şehir için hava durumu"""
    try:
        weather_data = get_weather(city)
        return jsonify({
            "success": True,
            "weather": weather_data
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
```

2. **Frontend'e fonksiyon ekleyin:**

```javascript
async function loadWeather(city) {
    const response = await fetch(`/api/weather/${city}`);
    const data = await response.json();
    if (data.success) {
        displayWeather(data.weather);
    }
}

function displayWeather(weather) {
    const html = `
        <div class="weather-widget">
            <div>${weather.current.temp_c}°C</div>
            <div>${weather.current.condition.text}</div>
        </div>
    `;
    document.getElementById('weatherContainer').innerHTML = html;
}
```

3. **requirements.txt güncelleme:**

```
python-dotenv==1.0.0
```

---

## Test Etme

### Manuel Test

1. Flask uygulamasını başlatın:
```bash
python app.py
```

2. Tarayıcıda `http://localhost:5000` adresini açın

3. Farklı senaryoları test edin:
   - Farklı başlangıç noktaları
   - Farklı bütçeler
   - Farklı gün sayıları
   - Farklı tercihler

### API Test Script

```bash
# Flask uygulamasını başka bir terminalde çalıştırın
python app.py

# Test script'ini çalıştırın
python test_api.py
```

### Unit Test (Gelecek)

```python
import unittest
from app import calculate_distance, calculate_transport_cost

class TestCalculations(unittest.TestCase):
    def test_distance(self):
        loc1 = {"lat": 39.9334, "lng": 32.8597}
        loc2 = {"lat": 41.0082, "lng": 28.9784}
        distance = calculate_distance(loc1, loc2)
        self.assertGreater(distance, 0)
    
    def test_transport_cost(self):
        cost = calculate_transport_cost(100, "basic")
        self.assertEqual(cost, 250)  # 100 km * 2.5 TL/km

if __name__ == '__main__':
    unittest.main()
```

---

## Deployment

### Heroku Deployment

1. **Procfile oluşturun:**
```
web: gunicorn app:app
```

2. **requirements.txt'e ekleyin:**
```
gunicorn==21.2.0
```

3. **Deploy:**
```bash
heroku create ecotravel-app
git push heroku main
heroku open
```

### Docker Deployment

1. **Dockerfile oluşturun:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

2. **Build ve run:**
```bash
docker build -t ecotravel .
docker run -p 5000:5000 ecotravel
```

### Production Ayarları

`app.py` dosyasının son satırını değiştirin:

```python
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(
        debug=os.environ.get('DEBUG', 'False') == 'True',
        host='0.0.0.0',
        port=port
    )
```

---

## Veritabanı Entegrasyonu (Gelecek)

### SQLite ile Başlangıç

```python
import sqlite3

def init_db():
    conn = sqlite3.connect('ecotravel.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS pois
                 (id INTEGER PRIMARY KEY,
                  name TEXT,
                  lat REAL,
                  lng REAL,
                  city TEXT,
                  category TEXT,
                  description TEXT,
                  visit_duration INTEGER,
                  cost_basic INTEGER,
                  cost_mid INTEGER,
                  cost_luxury INTEGER,
                  rating REAL)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS reviews
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  poi_id INTEGER,
                  rating INTEGER,
                  comment TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (poi_id) REFERENCES pois (id))''')
    
    conn.commit()
    conn.close()
```

---

## Güvenlik En İyi Uygulamaları

1. **Input Validation:**
```python
def validate_location(lat, lng):
    if not (-90 <= lat <= 90):
        raise ValueError("Invalid latitude")
    if not (-180 <= lng <= 180):
        raise ValueError("Invalid longitude")
```

2. **Environment Variables:**
```python
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
```

3. **CORS Configuration:**
```python
from flask_cors import CORS

CORS(app, resources={
    r"/api/*": {
        "origins": ["https://yourdomain.com"],
        "methods": ["GET", "POST"]
    }
})
```

---

## Performans Optimizasyonu

1. **Caching:**
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def calculate_distance(loc1_tuple, loc2_tuple):
    # Distance calculation
    pass
```

2. **Async Operations:**
```python
import asyncio
import aiohttp

async def fetch_multiple_pois(poi_ids):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_poi(session, poi_id) for poi_id in poi_ids]
        return await asyncio.gather(*tasks)
```

---

## Debugging

### Flask Debug Mode

```python
app.run(debug=True)
```

### Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.route('/api/plan', methods=['POST'])
def create_plan():
    logger.debug(f"Received request: {request.json}")
    # ...
```

### Browser DevTools

- Console: JavaScript hatalarını görmek için
- Network: API isteklerini izlemek için
- Elements: DOM değişikliklerini incelemek için

---

## Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun
3. Değişikliklerinizi commit edin
4. Branch'inizi push edin
5. Pull Request açın

### Commit Message Formatı

```
<type>: <subject>

<body>

<footer>
```

Types:
- feat: Yeni özellik
- fix: Bug düzeltmesi
- docs: Dokümantasyon
- style: Formatlama
- refactor: Kod iyileştirme
- test: Test ekleme
- chore: Bakım işleri

Örnek:
```
feat: Add weather integration

- Added weather API endpoint
- Integrated weather data into itinerary
- Updated UI to show weather forecasts

Closes #123
```

---

## Kaynaklar

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Leaflet.js Documentation](https://leafletjs.com/)
- [Python geopy](https://geopy.readthedocs.io/)
- [CSS Tricks](https://css-tricks.com/)

---

Son güncelleme: 2026-01-16
