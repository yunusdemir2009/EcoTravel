"""
Refactored and professional version of EcoTravel Flask application.
"""
import time
from flask import Flask, render_template, request, jsonify, g
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flasgger import Swagger
from marshmallow import ValidationError

from config import get_config
from logger import setup_logging, RequestLogger
from exceptions import EcoTravelException, ValidationError as CustomValidationError
from validators import validate_request, TravelPlanRequestSchema
from services import (
    TravelPlannerService,
    POIService,
    GeocodeService,
)


def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__)

    # Load configuration
    config_class = get_config(config_name)
    app.config.from_object(config_class)

    # Setup extensions
    setup_extensions(app)

    # Setup logging
    logger = setup_logging(app)
    request_logger = RequestLogger(app)

    # Register error handlers
    register_error_handlers(app)

    # Register request hooks
    register_request_hooks(app, request_logger)

    # Register routes
    register_routes(app)

    logger.info("EcoTravel application initialized successfully")

    return app


def setup_extensions(app):
    """Initialize Flask extensions"""
    # CORS
    CORS(app, origins=app.config["CORS_ORIGINS"])

    # Rate limiting
    if app.config["RATELIMIT_ENABLED"]:
        limiter = Limiter(
            app=app,
            key_func=get_remote_address,
            default_limits=[app.config["RATELIMIT_DEFAULT"]],
            storage_uri=app.config["RATELIMIT_STORAGE_URL"],
        )
        app.limiter = limiter

    # API Documentation with Swagger
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec",
                "route": "/apispec.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/api/docs/",
    }

    swagger_template = {
        "info": {
            "title": "EcoTravel API",
            "description": "Akıllı Gezi Planlayıcı API Dokümantasyonu",
            "version": "1.0.0",
            "contact": {
                "name": "EcoTravel Team",
            },
        },
        "schemes": ["http", "https"],
        "tags": [
            {"name": "Travel Planning", "description": "Seyahat planı oluşturma endpoint'leri"},
            {"name": "POI", "description": "İlgi çekici yerler (Points of Interest)"},
            {"name": "Geocoding", "description": "Konum servisleri"},
        ],
    }

    Swagger(app, config=swagger_config, template=swagger_template)


def register_error_handlers(app):
    """Register error handlers"""

    @app.errorhandler(EcoTravelException)
    def handle_custom_exception(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        app.logger.error(f"Custom exception: {error.message}", extra={"status_code": error.status_code})
        return response

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        app.logger.warning(f"Validation error: {error.messages}")
        return jsonify({"error": "Validation failed", "details": error.messages}), 400

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def handle_internal_error(error):
        app.logger.error(f"Internal server error: {str(error)}")
        return jsonify({"error": "Internal server error"}), 500

    @app.errorhandler(429)
    def handle_rate_limit(error):
        app.logger.warning(f"Rate limit exceeded: {request.remote_addr}")
        return jsonify({"error": "Rate limit exceeded. Please try again later."}), 429


def register_request_hooks(app, request_logger):
    """Register before/after request hooks"""

    @app.before_request
    def before_request():
        g.start_time = time.time()

    @app.after_request
    def after_request(response):
        if hasattr(g, "start_time"):
            duration_ms = (time.time() - g.start_time) * 1000
            request_logger.log_request(request, response, duration_ms)
        return response


def register_routes(app):
    """Register application routes"""

    @app.route("/")
    def index():
        """
        Ana sayfa
        ---
        tags:
          - Frontend
        responses:
          200:
            description: HTML sayfası döner
        """
        return render_template("index.html")

    @app.route("/api/plan", methods=["POST"])
    def create_travel_plan():
        """
        Seyahat planı oluşturma
        ---
        tags:
          - Travel Planning
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              required:
                - start_location
                - start_lat
                - start_lng
                - days
                - budget
              properties:
                start_location:
                  type: string
                  example: "Ankara"
                start_lat:
                  type: number
                  example: 39.9334
                start_lng:
                  type: number
                  example: 32.8597
                end_location:
                  type: string
                  example: "Antalya"
                end_lat:
                  type: number
                  example: 36.8969
                end_lng:
                  type: number
                  example: 30.7133
                days:
                  type: integer
                  example: 7
                budget:
                  type: number
                  example: 25000
                preferences:
                  type: array
                  items:
                    type: string
                  example: ["nature", "culture"]
        responses:
          200:
            description: Başarılı plan oluşturma
          400:
            description: Geçersiz istek
        """
        try:
            # Validate request
            data = validate_request(TravelPlanRequestSchema, request.json)

            # Create travel plan
            planner = TravelPlannerService()
            plans = planner.create_travel_plans(
                start_location=data["start_location"],
                start_lat=data["start_lat"],
                start_lng=data["start_lng"],
                end_location=data.get("end_location"),
                end_lat=data.get("end_lat"),
                end_lng=data.get("end_lng"),
                days=data["days"],
                budget=data["budget"],
                preferences=data.get("preferences", []),
            )

            app.logger.info(
                "Travel plan created",
                extra={
                    "start": data["start_location"],
                    "end": data.get("end_location"),
                    "days": data["days"],
                    "budget": data["budget"],
                },
            )

            return jsonify({"success": True, "plans": plans})

        except ValidationError as e:
            raise CustomValidationError(str(e.messages), payload={"validation_errors": e.messages})
        except Exception as e:
            app.logger.error(f"Error creating travel plan: {str(e)}")
            raise EcoTravelException(f"Plan oluşturulurken bir hata oluştu: {str(e)}")

    @app.route("/api/pois", methods=["GET"])
    def get_pois():
        """
        İlgi çekici yerleri getir
        ---
        tags:
          - POI
        parameters:
          - name: category
            in: query
            type: string
            description: Kategori filtresi
          - name: city
            in: query
            type: string
            description: Şehir filtresi
        responses:
          200:
            description: POI listesi
        """
        try:
            category = request.args.get("category")
            city = request.args.get("city")

            poi_service = POIService()
            pois = poi_service.get_pois(category=category, city=city)

            return jsonify({"success": True, "pois": pois})

        except Exception as e:
            app.logger.error(f"Error fetching POIs: {str(e)}")
            raise EcoTravelException("POI'ler getirilirken bir hata oluştu")

    @app.route("/api/geocode", methods=["POST"])
    def geocode_location():
        """
        Lokasyon adını koordinata çevir
        ---
        tags:
          - Geocoding
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              required:
                - location
              properties:
                location:
                  type: string
                  example: "Ankara, Kızılay"
        responses:
          200:
            description: Koordinatlar döner
          404:
            description: Lokasyon bulunamadı
        """
        try:
            location_name = request.json.get("location", "").strip()
            if not location_name:
                raise CustomValidationError("Location name is required")

            geocode_service = GeocodeService()
            result = geocode_service.geocode(location_name)

            if result:
                return jsonify({"success": True, **result})
            else:
                return jsonify({"success": False, "error": "Location not found"}), 404

        except Exception as e:
            app.logger.error(f"Geocoding error: {str(e)}")
            raise EcoTravelException("Geocoding işlemi başarısız oldu")

    @app.route("/api/reverse-geocode", methods=["POST"])
    def reverse_geocode():
        """
        Koordinatı lokasyon adına çevir
        ---
        tags:
          - Geocoding
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              required:
                - lat
                - lng
              properties:
                lat:
                  type: number
                  example: 39.9334
                lng:
                  type: number
                  example: 32.8597
        responses:
          200:
            description: Lokasyon adı döner
        """
        try:
            lat = request.json.get("lat")
            lng = request.json.get("lng")

            if lat is None or lng is None:
                raise CustomValidationError("Latitude and longitude are required")

            geocode_service = GeocodeService()
            location_name = geocode_service.reverse_geocode(lat, lng)

            return jsonify({"success": True, "location_name": location_name})

        except Exception as e:
            app.logger.error(f"Reverse geocoding error: {str(e)}")
            raise EcoTravelException("Reverse geocoding işlemi başarısız oldu")

    @app.route("/api/health", methods=["GET"])
    def health_check():
        """
        Sağlık kontrolü
        ---
        tags:
          - System
        responses:
          200:
            description: Sistem sağlıklı
        """
        return jsonify({"status": "healthy", "timestamp": time.time()})


# Create application instance
app = create_app()

if __name__ == "__main__":
    import os

    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode, host="0.0.0.0", port=5000)
