"""
Request validation schemas using marshmallow.
"""
from marshmallow import Schema, fields, validate, validates, ValidationError


class LocationSchema(Schema):
    """Schema for location data"""

    name = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    lat = fields.Float(required=True, validate=validate.Range(min=-90, max=90))
    lng = fields.Float(required=True, validate=validate.Range(min=-180, max=180))


class TravelPlanRequestSchema(Schema):
    """Schema for travel plan request"""

    start_location = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    start_lat = fields.Float(required=True, validate=validate.Range(min=-90, max=90))
    start_lng = fields.Float(required=True, validate=validate.Range(min=-180, max=180))

    end_location = fields.Str(allow_none=True, validate=validate.Length(max=200))
    end_lat = fields.Float(allow_none=True, validate=validate.Range(min=-90, max=90))
    end_lng = fields.Float(allow_none=True, validate=validate.Range(min=-180, max=180))

    days = fields.Int(required=True, validate=validate.Range(min=1, max=30))
    budget = fields.Float(required=True, validate=validate.Range(min=1000, max=1000000))

    preferences = fields.List(
        fields.Str(validate=validate.OneOf(["nature", "culture", "gastronomy", "adventure", "relaxation"])),
        required=False,
        load_default=[],
    )

    @validates("end_location")
    def validate_end_location(self, value):
        """Validate that if end_location is provided, coordinates are also provided"""
        if value:
            data = self.context.get("data", {})
            if not data.get("end_lat") or not data.get("end_lng"):
                raise ValidationError("End coordinates required when end_location is provided")


class POIFilterSchema(Schema):
    """Schema for POI filtering"""

    category = fields.Str(validate=validate.OneOf(["nature", "culture", "gastronomy", "adventure", "all"]))
    min_rating = fields.Float(validate=validate.Range(min=0, max=5))
    max_cost = fields.Float(validate=validate.Range(min=0))
    city = fields.Str(validate=validate.Length(max=100))


class FeedbackSchema(Schema):
    """Schema for user feedback"""

    poi_id = fields.Int(required=True, validate=validate.Range(min=1))
    rating = fields.Float(required=True, validate=validate.Range(min=1, max=5))
    comment = fields.Str(validate=validate.Length(max=1000))
    user_name = fields.Str(validate=validate.Length(max=100))


def validate_request(schema_class, data):
    """
    Validate request data against a schema
    
    Args:
        schema_class: Marshmallow schema class
        data: Dictionary to validate
        
    Returns:
        Validated and cleaned data
        
    Raises:
        ValidationError: If validation fails
    """
    schema = schema_class(context={"data": data})
    return schema.load(data)
