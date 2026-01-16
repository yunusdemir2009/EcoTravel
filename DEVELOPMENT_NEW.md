# 🚀 EcoTravel Geliştirme Kılavuzu

## Hızlı Başlangıç

### 1. Geliştirme Ortamını Hazırlama

```bash
# Virtual environment
python -m venv venv
source venv/bin/activate

# Dependencies
pip install -r requirements.txt

# Environment
cp .env.example .env
```

### 2. Yeni Profesyonel Yapıya Geçiş

Projede iki versiyon mevcut:
- `app.py` - Eski monolitik yapı (geriye uyumluluk için)
- `app_new.py` - Yeni profesyonel yapı (önerilen)

Yeni yapıyı kullanmak için:

```bash
# app_new.py'yi app.py yerine kullan
python app_new.py

# VEYA ortam değişkeni ile
export FLASK_APP=app_new.py
flask run
```

## 📁 Yeni Dosya Yapısı

### Core Files

- **config.py**: Environment-based configuration
  ```python
  from config import get_config
  config = get_config('development')
  ```

- **services.py**: Business logic
  - `TravelPlannerService`: Plan oluşturma
  - `POIService`: İlgi noktaları
  - `GeocodeService`: Lokasyon servisleri
  - `AccommodationService`: Konaklama
  - `TransportService`: Ulaşım

- **validators.py**: Input validation
  ```python
  from validators import validate_request, TravelPlanRequestSchema
  data = validate_request(TravelPlanRequestSchema, request.json)
  ```

- **exceptions.py**: Custom exceptions
  ```python
  from exceptions import ValidationError, ResourceNotFoundError
  raise ValidationError("Invalid input")
  ```

- **logger.py**: Logging configuration
  ```python
  from logger import setup_logging
  logger = setup_logging(app)
  ```

- **data.py**: Data models ve constants

## 🛠️ Development Workflow

### 1. Yeni Feature Geliştirme

```bash
# Feature branch
git checkout -b feature/my-feature

# Kod yazın
# ...

# Format ve lint
black .
isort .
flake8 .

# Test
pytest

# Commit
git add .
git commit -m "feat: Add my feature"
git push origin feature/my-feature
```

### 2. Kod Kalitesi Standartları

#### Black Formatting
```bash
# Otomatik format
black .

# Sadece kontrol (CI'da)
black --check --diff .
```

#### Import Sorting
```bash
# Otomatik sort
isort .

# Sadece kontrol
isort --check-only --diff .
```

#### Linting
```bash
# Flake8
flake8 .

# Pylint
pylint **/*.py
```

### 3. Testing

```bash
# Tüm testler
pytest -v

# Coverage
pytest --cov=. --cov-report=html
open htmlcov/index.html

# Specific test
pytest tests/test_api.py::test_create_plan -v

# Watch mode
pytest-watch
```

## 📝 Kod Yazma Standartları

### Docstrings

```python
def calculate_transport_cost(distance_km: float, tier: str) -> float:
    """
    Calculate transportation cost based on distance and tier.
    
    Args:
        distance_km: Distance in kilometers
        tier: Service tier ('basic', 'mid', 'luxury')
        
    Returns:
        float: Transportation cost in TRY
        
    Raises:
        ValidationError: If tier is invalid
    """
    pass
```

### Type Hints

```python
from typing import Dict, List, Optional, Tuple

def create_plan(
    start_loc: Dict[str, float],
    days: int,
    preferences: List[str]
) -> Dict:
    """Type hints kullanın"""
    pass
```

### Error Handling

```python
from exceptions import ValidationError, ResourceNotFoundError

def get_poi(poi_id: int) -> Dict:
    """Proper exception handling"""
    poi = poi_service.get_poi_by_id(poi_id)
    if not poi:
        raise ResourceNotFoundError(f"POI {poi_id} not found")
    return poi
```

### Logging

```python
app.logger.info(
    "Plan created successfully",
    extra={
        "user_id": user_id,
        "days": days,
        "budget": budget
    }
)

app.logger.error(
    f"Failed to create plan: {str(e)}",
    exc_info=True
)
```

## 🔧 Configuration Management

### Environment Variables

`.env` dosyası:
```bash
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=dev-secret-key

# Custom settings
DEFAULT_CITY=Ankara
POI_SEARCH_RADIUS_KM=100
```

### Config Classes

```python
from config import DevelopmentConfig, ProductionConfig

# Development
app.config.from_object(DevelopmentConfig)

# Production
app.config.from_object(ProductionConfig)
```

## 🧪 Testing Patterns

### Unit Test Örneği

```python
import pytest
from services import TransportService

def test_calculate_transport_cost():
    """Test transport cost calculation"""
    service = TransportService()
    
    # Test city transport
    cost = service.calculate_transport_cost(3.5, 'basic')
    assert cost == 50
    
    # Test intercity
    cost = service.calculate_transport_cost(400, 'luxury')
    assert cost == 14000
```

### API Test Örneği

```python
def test_create_plan_api(client):
    """Test plan creation endpoint"""
    response = client.post('/api/plan', json={
        'start_location': 'Ankara',
        'start_lat': 39.9334,
        'start_lng': 32.8597,
        'days': 5,
        'budget': 15000,
        'preferences': ['nature']
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'plans' in data
```

## 🐳 Docker Development

### Local Build ve Test

```bash
# Build
docker build -t ecotravel:dev .

# Run
docker run -d -p 5000:5000 \
  -e FLASK_ENV=development \
  -v $(pwd):/app \
  ecotravel:dev

# Logs
docker logs -f ecotravel-dev

# Shell access
docker exec -it ecotravel-dev /bin/bash
```

### Docker Compose

```bash
# Development
docker-compose up

# Production (with nginx)
docker-compose --profile production up

# Rebuild
docker-compose up --build

# Down
docker-compose down -v
```

## 📊 Monitoring ve Logging

### Log Dosyaları

```bash
# Tüm loglar
tail -f logs/ecotravel.log

# JSON format parse
cat logs/ecotravel.log | jq '.message'

# Error logları
cat logs/ecotravel.log | jq 'select(.levelname=="ERROR")'
```

### Health Check

```bash
# Local
curl http://localhost:5000/api/health

# Docker
docker exec ecotravel-app curl http://localhost:5000/api/health
```

## 🚀 Deployment

### Pre-deployment Checklist

- [ ] Tüm testler passing
- [ ] Code formatted (black, isort)
- [ ] Linting passing (flake8, pylint)
- [ ] Environment variables configured
- [ ] SECRET_KEY değiştirildi
- [ ] DEBUG=False
- [ ] Logs directory writable
- [ ] Database migrations (if any)

### Production Deployment

```bash
# Build production image
docker build -t ecotravel:v1.0.0 .

# Test production image
docker run -d -p 5000:5000 \
  -e FLASK_ENV=production \
  -e FLASK_DEBUG=False \
  -e SECRET_KEY=$SECRET_KEY \
  ecotravel:v1.0.0

# Deploy with docker-compose
docker-compose --profile production up -d

# Check health
curl http://your-domain.com/api/health
```

## 🔍 Debugging

### VS Code Launch Configuration

`.vscode/launch.json`:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Flask",
            "type": "python",
            "request": "launch",
            "module": "flask",
            "env": {
                "FLASK_APP": "app_new.py",
                "FLASK_ENV": "development",
                "FLASK_DEBUG": "1"
            },
            "args": ["run", "--no-debugger", "--no-reload"],
            "jinja": true
        }
    ]
}
```

### Debug Logging

```python
# Temporary debug logs
app.logger.debug(f"Request data: {request.json}")
app.logger.debug(f"Service response: {response}")

# Remember to remove or use proper log levels
```

## 📚 Useful Commands

```bash
# Pip
pip list --outdated
pip install -U package-name

# Find TODOs
grep -r "TODO" --include="*.py" .

# Code statistics
cloc . --exclude-dir=venv,node_modules

# Find large files
find . -type f -size +1M -not -path "*/venv/*"

# Database (if added later)
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## 🤝 Contribution Guidelines

1. **Branch naming**: `feature/`, `bugfix/`, `hotfix/`
2. **Commit messages**: Conventional commits
   - `feat:` Yeni özellik
   - `fix:` Bug fix
   - `docs:` Dokümantasyon
   - `style:` Formatting
   - `refactor:` Code refactoring
   - `test:` Test ekleme
   - `chore:` Maintenance

3. **Pull Request**:
   - Descriptive title
   - Clear description
   - Link to issue
   - Screenshots if UI change
   - Tests added
   - All checks passing

## 🐛 Common Issues

### Import Errors
```bash
# Solution: Add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Port Already in Use
```bash
# Find process
lsof -i :5000

# Kill process
kill -9 <PID>
```

### Docker Permission Issues
```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

---

💡 **Tip**: Bu kılavuzu düzenli güncelleyin!
