# EcoTravel API Dokumentasyonu

## API Endpoints

### 1. Ana Sayfa
**Endpoint:** `/`  
**Method:** GET  
**Açıklama:** Ana HTML sayfasını döndürür

**Response:**
```html
HTML sayfası
```

---

### 2. Gezi Planı Oluştur
**Endpoint:** `/api/plan`  
**Method:** POST  
**Açıklama:** Kullanıcı parametrelerine göre üç seviyede gezi planı oluşturur

**Request Body:**
```json
{
  "start_location": {
    "lat": 39.9334,
    "lng": 32.8597
  },
  "end_location": {
    "lat": 41.0082,
    "lng": 28.9784
  },
  "days": 5,
  "budget": 5000,
  "preferences": ["nature", "culture"]
}
```

**Request Parameters:**
| Parametre | Tip | Zorunlu | Açıklama |
|-----------|-----|---------|----------|
| start_location | Object | Evet | Başlangıç konumu (lat, lng) |
| end_location | Object | Hayır | Hedef konum (lat, lng). Belirtilmezse gidiş-dönüş |
| days | Integer | Evet | Gezi süresi (1-30 gün) |
| budget | Float | Evet | Bütçe (TL) |
| preferences | Array | Hayır | Gezi tercihleri ["nature", "culture", "gastronomy"] |

**Response:**
```json
{
  "success": true,
  "plans": {
    "basic": {
      "tier": "basic",
      "tier_name": "Ekonomik Plan",
      "total_days": 5,
      "estimated_cost": 3250.50,
      "min_cost": 2925.45,
      "max_cost": 3575.55,
      "fits_budget": true,
      "itinerary": [
        {
          "day": 1,
          "date": "2026-01-16",
          "activities": [
            {
              "name": "Anıtkabir",
              "description": "Atatürk'ün anıt mezarı",
              "duration": 2,
              "cost": 50.0,
              "category": "culture",
              "location": {
                "lat": 39.9250,
                "lng": 32.8369
              }
            }
          ],
          "accommodation": {
            "name": "Hostel",
            "cost_per_night": 150
          },
          "food_cost": 200,
          "daily_cost": 400.0
        }
      ]
    },
    "mid": { /* Orta seviye plan */ },
    "luxury": { /* Lüks plan */ }
  }
}
```

---

### 3. POI Listesi
**Endpoint:** `/api/pois`  
**Method:** GET  
**Açıklama:** Tüm gezilecek yerleri (Points of Interest) döndürür

**Response:**
```json
{
  "success": true,
  "pois": [
    {
      "id": 1,
      "name": "Anıtkabir",
      "location": {
        "lat": 39.9250,
        "lng": 32.8369
      },
      "city": "Ankara",
      "category": "culture",
      "description": "Atatürk'ün anıt mezarı",
      "visit_duration": 2,
      "cost_basic": 0,
      "cost_mid": 50,
      "cost_luxury": 150,
      "rating": 4.8
    }
  ]
}
```

---

### 4. Yorum Gönder
**Endpoint:** `/api/review`  
**Method:** POST  
**Açıklama:** Bir POI için yorum ve puanlama gönderir

**Request Body:**
```json
{
  "poi_id": 1,
  "rating": 5,
  "comment": "Harika bir deneyimdi!"
}
```

**Request Parameters:**
| Parametre | Tip | Zorunlu | Açıklama |
|-----------|-----|---------|----------|
| poi_id | Integer | Evet | POI ID |
| rating | Integer | Evet | Puan (1-5) |
| comment | String | Evet | Yorum metni |

**Response:**
```json
{
  "success": true,
  "message": "Yorum başarıyla gönderildi"
}
```

---

### 5. Konum Geocoding
**Endpoint:** `/api/geocode`  
**Method:** POST  
**Açıklama:** Şehir/ilçe/mahalle adını koordinatlara dönüştürür

**Request Body:**
```json
{
  "location": "İstanbul, Beyoğlu"
}
```

**Request Parameters:**
| Parametre | Tip | Zorunlu | Açıklama |
|-----------|-----|---------|----------|
| location | String | Evet | Şehir, ilçe veya mahalle adı |

**Response:**
```json
{
  "success": true,
  "location": {
    "lat": 41.0370,
    "lng": 28.9784,
    "display_name": "Beyoğlu, İstanbul"
  }
}
```

**Desteklenen Konumlar:**
- 30+ Türk şehri ve ilçesi (Ankara, İstanbul, İzmir, Antalya, Bursa, vb.)
- Mahalle ve semt isimleri (Beyoğlu, Kadıköy, Çankaya, Kızılay, vb.)
- Fallback: OpenStreetMap Nominatim geocoding servisi

---

### 6. Reverse Geocoding
**Endpoint:** `/api/reverse-geocode`  
**Method:** POST  
**Açıklama:** Koordinatları şehir/ilçe adına dönüştürür

**Request Body:**
```json
{
  "lat": 39.9334,
  "lng": 32.8597
}
```

**Request Parameters:**
| Parametre | Tip | Zorunlu | Açıklama |
|-----------|-----|---------|----------|
| lat | Float | Evet | Enlem |
| lng | Float | Evet | Boylam |

**Response:**
```json
{
  "success": true,
  "location_name": "Ankara"
}
```

---

## Hata Yanıtları

Tüm endpoint'ler hata durumunda şu formatta yanıt döner:

```json
{
  "success": false,
  "error": "Hata mesajı"
}
```

**HTTP Status Kodları:**
- `200`: Başarılı
- `400`: Geçersiz istek
- `404`: Bulunamadı
- `500`: Sunucu hatası

---

## Veri Modelleri

### Location
```json
{
  "lat": 39.9334,  // Enlem (latitude)
  "lng": 32.8597   // Boylam (longitude)
}
```

### POI (Point of Interest)
```json
{
  "id": 1,
  "name": "Yer adı",
  "location": { "lat": 0.0, "lng": 0.0 },
  "city": "Şehir",
  "category": "nature|culture|gastronomy",
  "description": "Açıklama",
  "visit_duration": 2,  // saat
  "cost_basic": 0,
  "cost_mid": 50,
  "cost_luxury": 150,
  "rating": 4.8
}
```

### Activity
```json
{
  "name": "Aktivite adı",
  "description": "Açıklama",
  "duration": 2,  // saat
  "cost": 50.0,  // TL
  "category": "nature|culture|gastronomy",
  "location": { "lat": 0.0, "lng": 0.0 }
}
```

### Accommodation
```json
{
  "name": "Konaklama adı",
  "cost_per_night": 150  // TL
}
```

### Day Itinerary
```json
{
  "day": 1,
  "date": "2026-01-16",
  "activities": [/* Activity listesi */],
  "accommodation": {/* Accommodation */},
  "food_cost": 200,
  "daily_cost": 400.0
}
```

---

## Kullanım Örnekleri

### Örnek 1: Ankara'dan İstanbul'a 5 Günlük Ekonomik Gezi
```bash
curl -X POST http://localhost:5000/api/plan \
  -H "Content-Type: application/json" \
  -d '{
    "start_location": {"lat": 39.9334, "lng": 32.8597},
    "end_location": {"lat": 41.0082, "lng": 28.9784},
    "days": 5,
    "budget": 5000,
    "preferences": ["culture"]
  }'
```

### Örnek 2: Gidiş-Dönüş Doğa Gezisi
```bash
curl -X POST http://localhost:5000/api/plan \
  -H "Content-Type: application/json" \
  -d '{
    "start_location": {"lat": 39.9334, "lng": 32.8597},
    "days": 3,
    "budget": 3000,
    "preferences": ["nature"]
  }'
```

### Örnek 3: Tüm POI'ları Getir
```bash
curl http://localhost:5000/api/pois
```

### Örnek 4: Yorum Gönder
```bash
curl -X POST http://localhost:5000/api/review \
  -H "Content-Type: application/json" \
  -d '{
    "poi_id": 1,
    "rating": 5,
    "comment": "Muhteşem bir yer!"
  }'
```

### Örnek 5: Şehir Adını Geocode Et
```bash
curl -X POST http://localhost:5000/api/geocode \
  -H "Content-Type: application/json" \
  -d '{
    "location": "İstanbul, Kadıköy"
  }'
```

### Örnek 6: Koordinatları Şehir Adına Çevir
```bash
curl -X POST http://localhost:5000/api/reverse-geocode \
  -H "Content-Type: application/json" \
  -d '{
    "lat": 41.0082,
    "lng": 28.9784
  }'
```

---

## Rate Limiting
Şu anda rate limiting uygulanmamaktadır. Gelecekte eklenebilir.

## Versiyon
API Version: 1.0.0

## Güvenlik
- CORS etkin
- Input validation yapılmaktadır
- SQL injection koruması (şu an veritabanı kullanılmıyor)

---

Son güncelleme: 2026-01-16
