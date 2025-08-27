import pytest
import httpx
from unittest.mock import AsyncMock, patch
from app.services.binance_service import BinanceService

@pytest.fixture
def binance_service():
    return BinanceService()

@pytest.mark.asyncio
async def test_get_btc_prices_success(binance_service):
    mock_response_data = {"symbol": "BTCUSDT", "price": "45000.00"}
    
    with patch.object(httpx.AsyncClient, 'get') as mock_get:
        mock_response = AsyncMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        rates = await binance_service.get_btc_prices(force_refresh=True)
        
        assert "BTCUSDT" in rates
        assert rates["BTCUSDT"] == 45000.00

@pytest.mark.asyncio
async def test_get_btc_prices_cached(binance_service):
    binance_service._cached_rates = {"BTCUSDT": 45000.00}
    binance_service._last_fetch = binance_service._last_fetch or binance_service.datetime.utcnow()
    
    rates = await binance_service.get_btc_prices()
    
    assert "BTCUSDT" in rates
    assert rates["BTCUSDT"] == 45000.00

@pytest.mark.asyncio
async def test_fetch_single_price_success(binance_service):
    mock_response_data = {"symbol": "BTCUSDT", "price": "45000.00"}
    
    with patch.object(httpx.AsyncClient, 'get') as mock_get:
        mock_response = AsyncMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        client = await binance_service._get_client()
        symbol, price = await binance_service._fetch_single_price(client, "BTCUSDT")
        
        assert symbol == "BTCUSDT"
        assert price == 45000.00

@pytest.mark.asyncio
async def test_fetch_single_price_failure(binance_service):
    with patch.object(httpx.AsyncClient, 'get') as mock_get:
        mock_get.side_effect = httpx.RequestError("Connection error")
        
        client = await binance_service._get_client()
        symbol, price = await binance_service._fetch_single_price(client, "BTCUSDT")
        
        assert symbol == "BTCUSDT"
        assert price is None

def test_get_currency_from_pair(binance_service):
    assert binance_service.get_currency_from_pair("BTCUSDT") == "USDT"
    assert binance_service.get_currency_from_pair("BTCEUR") == "EUR"
    assert binance_service.get_currency_from_pair("BTCGBP") == "GBP"
    assert binance_service.get_currency_from_pair("INVALID") == ""

@pytest.mark.asyncio
async def test_get_supported_currencies(binance_service):
    currencies = await binance_service.get_supported_currencies()
    
    expected_currencies = ["AUD", "CAD", "CHF", "DKK", "EUR", "GBP", "JPY", "NOK", "PLN", "SEK", "USDT", "ZAR"]
    
    assert set(currencies) == set(expected_currencies)