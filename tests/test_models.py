import pytest
from pydantic import ValidationError

from app.models.response import ConversionResponse


def test_conversion_response_valid():
    """Test valid ConversionResponse creation."""
    response = ConversionResponse(quantity=100.50, ccy="USD")

    assert response.quantity == 100.50
    assert response.ccy == "USD"


def test_conversion_response_dict():
    """Test ConversionResponse conversion to dict."""
    response = ConversionResponse(quantity=100.50, ccy="USD")

    data = response.dict()
    assert data == {"quantity": 100.50, "ccy": "USD"}


def test_conversion_response_json():
    """Test ConversionResponse JSON serialization."""
    response = ConversionResponse(quantity=100.50, ccy="USD")

    json_data = response.json()
    assert '"quantity":100.5' in json_data or '"quantity": 100.5' in json_data
    assert '"ccy":"USD"' in json_data or '"ccy": "USD"' in json_data


def test_conversion_response_validation_error():
    """Test ConversionResponse validation with invalid data."""
    with pytest.raises(ValidationError):
        ConversionResponse(quantity="invalid", ccy="USD")

    with pytest.raises(ValidationError):
        ConversionResponse(quantity=100.50, ccy=123)
