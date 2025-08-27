import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from main import app

client = TestClient(app)

@pytest.fixture
def mock_fx_service():
    with patch("main.fx_service") as mock:
        yield mock

def test_health_check():
    response = client.get("/health")
    
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "currency-converter"}

def test_convert_currency_success(mock_fx_service):
    mock_fx_service.convert = AsyncMock(return_value=779.77)
    
    response = client.get("/convert?ccy_from=USD&ccy_to=GBP&quantity=1000")
    
    assert response.status_code == 200
    assert response.json() == {"quantity": 779.77, "ccy": "GBP"}
    mock_fx_service.convert.assert_called_once_with(
        from_currency="USD",
        to_currency="GBP", 
        amount=1000.0
    )

def test_convert_currency_missing_parameters():
    response = client.get("/convert?ccy_from=USD&quantity=1000")
    
    assert response.status_code == 422

def test_convert_currency_negative_amount():
    response = client.get("/convert?ccy_from=USD&ccy_to=GBP&quantity=-1000")
    
    assert response.status_code == 422

def test_convert_currency_zero_amount():
    response = client.get("/convert?ccy_from=USD&ccy_to=GBP&quantity=0")
    
    assert response.status_code == 422

def test_convert_currency_invalid_currency(mock_fx_service):
    mock_fx_service.convert = AsyncMock(side_effect=ValueError("Currency XYZ not supported"))
    
    response = client.get("/convert?ccy_from=XYZ&ccy_to=GBP&quantity=1000")
    
    assert response.status_code == 400
    assert "Currency XYZ not supported" in response.json()["detail"]

def test_convert_currency_service_error(mock_fx_service):
    mock_fx_service.convert = AsyncMock(side_effect=Exception("Service unavailable"))
    
    response = client.get("/convert?ccy_from=USD&ccy_to=GBP&quantity=1000")
    
    assert response.status_code == 500
    assert response.json()["detail"] == "Internal server error"

def test_convert_currency_case_insensitive(mock_fx_service):
    mock_fx_service.convert = AsyncMock(return_value=779.77)
    
    response = client.get("/convert?ccy_from=usd&ccy_to=gbp&quantity=1000")
    
    assert response.status_code == 200
    mock_fx_service.convert.assert_called_once_with(
        from_currency="USD",
        to_currency="GBP",
        amount=1000.0
    )