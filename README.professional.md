# 🌍 EcoTravel - Profesyonel Akıllı Gezi Planlayıcı

[![CI/CD](https://github.com/yunusdemir2009/EcoTravel/workflows/CI%2FCD%20Pipeline/badge.svg)](https://github.com/yunusdemir2009/EcoTravel/actions)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

EcoTravel, kullanıcıların bütçelerine ve zamanlarına göre kişiselleştirilmiş seyahat planları oluşturmalarını sağlayan **profesyonel** bir gezi planlama uygulamasıdır.

## 🚀 Yeni Profesyonel Özellikler

### Kod Kalitesi
- ✅ **Black** formatlaması ile tutarlı kod stili
- ✅ **Flake8** ve **Pylint** ile statik kod analizi
- ✅ **isort** ile düzenli import yapısı
- ✅ **Type hints** desteği
- ✅ Yapılandırılmış exception handling

### Güvenlik ve Validasyon
- ✅ **Marshmallow** ile input validation
- ✅ **Flask-Limiter** ile rate limiting
- ✅ Environment-based configuration
- ✅ Structured logging (JSON format)
- ✅ Custom exception handling

### DevOps ve Deployment
- ✅ **Docker** containerization
- ✅ **Docker Compose** orchestration
- ✅ **Nginx** reverse proxy konfigürasyonu
- ✅ **GitHub Actions** CI/CD pipeline
- ✅ **Gunicorn** production server
- ✅ Health check endpoints

### API ve Dokümantasyon
- ✅ **Swagger/OpenAPI** otomatik dokümantasyon
- ✅ RESTful API tasarımı
- ✅ Yapılandırılmış error responses
- ✅ Request/response logging

### Mimari İyileştirmeler
- ✅ **Service Layer Pattern** - İş mantığı ayrımı
- ✅ **Configuration Management** - Environment-based config
- ✅ **Data Layer** - Ayrı data modelleri
- ✅ **Application Factory Pattern** - Modüler yapı

## ✨ Temel Özellikler

### 1. Konum Bazlı Planlama
- GPS veya manuel konum girişi ile başlangıç noktası belirleme
- İsteğe bağlı hedef konum seçimi
- Gidiş-dönüş veya tek yön rotalar

### 2. Üç Farklı Seviye Plan
- **Ekonomik Plan (Basic)**: En uygun fiyatlı seçenekler
- **Orta Seviye Plan**: Konforlu ama ekonomik seçenekler
- **Lüks Plan**: Maksimum konfor ve deneyim

### 3. Akıllı Rota Önerisi
- Rota üzerindeki gezilecek yerler (POI)
- Etkinlik önerileri
- Konaklama önerileri
- Yemek ve ulaşım planlaması

## 📋 Gereksinimler

- Python 3.11+
- Docker ve Docker Compose (opsiyonel)
- Modern web tarayıcı

## 🛠️ Kurulum

### Yerel Kurulum (Development)

```bash
# 1. Repository'yi klonlayın
git clone https://github.com/yunusdemir2009/EcoTravel.git
cd EcoTravel

# 2. Virtual environment oluşturun
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Bağımlılıkları yükleyin
pip install -r requirements.txt

# 4. Environment dosyası oluşturun
cp .env.example .env
# .env dosyasını düzenleyin

# 5. Uygulamayı çalıştırın
python app.py

# VEYA development mode için:
export FLASK_ENV=development
export FLASK_DEBUG=True
flask run
```

### Docker ile Kurulum (Production)

```bash
# 1. Docker image build edin
docker build -t ecotravel:latest .

# 2. Container çalıştırın
docker run -d -p 5000:5000 --name ecotravel ecotravel:latest

# VEYA Docker Compose ile:
docker-compose up -d

# Nginx ile (production):
docker-compose --profile production up -d
```

## 🚀 Kullanım

### Web Arayüzü
Tarayıcınızda şu adresi açın: `http://localhost:5000`

### API Dokümantasyonu
Swagger UI: `http://localhost:5000/api/docs`

### API Örnekleri

#### Seyahat Planı Oluşturma
```bash
curl -X POST http://localhost:5000/api/plan \
  -H "Content-Type: application/json" \
  -d '{
    "start_location": "Ankara",
    "start_lat": 39.9334,
    "start_lng": 32.8597,
    "end_location": "Antalya",
    "end_lat": 36.8969,
    "end_lng": 30.7133,
    "days": 7,
    "budget": 25000,
    "preferences": ["nature", "culture"]
  }'
```

#### Lokasyon Geocoding
```bash
curl -X POST http://localhost:5000/api/geocode \
  -H "Content-Type: application/json" \
  -d '{"location": "Ankara, Kızılay"}'
```

#### Health Check
```bash
curl http://localhost:5000/api/health
```

## 🧪 Testing

```bash
# Tüm testleri çalıştır
pytest

# Coverage ile
pytest --cov=. --cov-report=html

# Sadece belirli bir test
pytest tests/test_api.py -v
```

## 🔍 Kod Kalitesi Kontrolleri

```bash
# Code formatting (otomatik düzeltme)
black .

# Import sorting (otomatik düzeltme)
isort .

# Linting (kontrol)
flake8 .
pylint **/*.py

# Tüm kontrolleri bir arada
black . && isort . && flake8 . && pytest
```

## 📊 Proje Yapısı

```
EcoTravel/
├── app.py                 # Ana uygulama (eski - uyumluluk için)
├── app_new.py            # Yeni profesyonel uygulama
├── config.py             # Configuration management
├── data.py               # Data models ve constants
├── services.py           # Business logic layer
├── validators.py         # Input validation schemas
├── exceptions.py         # Custom exceptions
├── logger.py             # Logging configuration
├── requirements.txt      # Python dependencies
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Docker Compose config
├── nginx.conf           # Nginx reverse proxy config
├── pyproject.toml       # Python project config
├── .flake8             # Flake8 config
├── .pylintrc           # Pylint config
├── .env.example        # Environment variables template
├── .github/
│   └── workflows/
│       └── ci-cd.yml   # GitHub Actions pipeline
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
├── templates/
│   └── index.html
├── tests/
│   └── test_api.py
└── logs/               # Application logs (gitignored)
```

## 🔐 Güvenlik

- ✅ Environment variables ile hassas veri yönetimi
- ✅ Rate limiting ile API koruması
- ✅ Input validation ile injection saldırılarına karşı koruma
- ✅ CORS politikaları
- ✅ Structured logging ile audit trail

## 🌍 Environment Variables

Önemli environment variables (`.env` dosyasında):

```bash
# Flask
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here

# Application
DEFAULT_CITY=Ankara
POI_SEARCH_RADIUS_KM=100
MAX_TRAVEL_DAYS=30

# Rate Limiting
RATELIMIT_ENABLED=True
RATELIMIT_DEFAULT=100 per hour

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/ecotravel.log
```

## 📈 CI/CD Pipeline

GitHub Actions otomatik olarak şunları çalıştırır:

1. **Code Quality Checks**
   - Black formatting
   - Flake8 linting
   - isort import sorting
   - Pylint analysis

2. **Testing**
   - Unit tests
   - Coverage reports

3. **Security Scanning**
   - Bandit security scan

4. **Docker Build**
   - Image build
   - Container health check

## 🚀 Production Deployment

### Gunicorn ile Production Server

```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app
```

### Systemd Service (Linux)

```bash
sudo cp ecotravel.service /etc/systemd/system/
sudo systemctl enable ecotravel
sudo systemctl start ecotravel
```

### Nginx Reverse Proxy

```bash
# nginx.conf dosyasını kullanın
sudo cp nginx.conf /etc/nginx/sites-available/ecotravel
sudo ln -s /etc/nginx/sites-available/ecotravel /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 📝 API Endpoint'leri

| Endpoint | Method | Açıklama |
|----------|--------|----------|
| `/` | GET | Ana sayfa |
| `/api/plan` | POST | Seyahat planı oluştur |
| `/api/pois` | GET | POI listesi |
| `/api/geocode` | POST | Lokasyon → Koordinat |
| `/api/reverse-geocode` | POST | Koordinat → Lokasyon |
| `/api/health` | GET | Health check |
| `/api/docs` | GET | Swagger UI |

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some AmazingFeature'`)
4. Branch'inizi push edin (`git push origin feature/AmazingFeature`)
5. Pull Request oluşturun

**Kod standartları:**
- Black formatlaması kullanın
- Flake8 ve Pylint kontrollerinden geçin
- Unit testler ekleyin
- Docstring'ler ekleyin

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 👥 İletişim

Proje Sahibi: yunusdemir2009
GitHub: [https://github.com/yunusdemir2009/EcoTravel](https://github.com/yunusdemir2009/EcoTravel)

## 🙏 Teşekkürler

- Flask framework
- Leaflet.js for maps
- Geopy for geocoding
- Bootstrap for UI components

## 📚 Ek Kaynaklar

- [API Dokümantasyonu](API.md)
- [Geliştirme Kılavuzu](DEVELOPMENT.md)
- [Swagger UI](http://localhost:5000/api/docs)

---

⭐ Projeyi beğendiyseniz yıldız vermeyi unutmayın!
