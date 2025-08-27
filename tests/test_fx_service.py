import pytest
from unittest.mock import AsyncMock
from app.services.fx_service import FXService
from app.services.binance_service import BinanceService

@pytest.fixture
def mock_binance_service():
    return AsyncMock(spec=BinanceService)

@pytest.fixture
def fx_service(mock_binance_service):
    return FXService(mock_binance_service)

@pytest.mark.asyncio
async def test_convert_same_currency(fx_service):
    result = await fx_service.convert("USD", "USD", 1000.0)
    assert result == 1000.0

@pytest.mark.asyncio
async def test_convert_different_currencies(fx_service, mock_binance_service):
    mock_binance_service.get_btc_prices.return_value = {
        "BTCUSDT": 45000.0,  # USD maps to USDT
        "BTCGBP": 35000.0
    }
    
    result = await fx_service.convert("USD", "GBP", 1000.0)
    
    expected_rate = 45000.0 / 35000.0
    expected_result = 1000.0 * expected_rate
    
    assert result == pytest.approx(expected_result, rel=1e-6)
    mock_binance_service.get_btc_prices.assert_called_once()

@pytest.mark.asyncio
async def test_convert_invalid_amount(fx_service):
    with pytest.raises(ValueError, match="Amount must be greater than 0"):
        await fx_service.convert("USD", "GBP", -100.0)
    
    with pytest.raises(ValueError, match="Amount must be greater than 0"):
        await fx_service.convert("USD", "GBP", 0.0)

@pytest.mark.asyncio
async def test_convert_unsupported_from_currency(fx_service, mock_binance_service):
    mock_binance_service.get_btc_prices.return_value = {
        "BTCGBP": 35000.0
    }
    
    with pytest.raises(ValueError, match="Currency XYZ not supported"):
        await fx_service.convert("XYZ", "GBP", 1000.0)

@pytest.mark.asyncio
async def test_convert_unsupported_to_currency(fx_service, mock_binance_service):
    mock_binance_service.get_btc_prices.return_value = {
        "BTCUSDT": 45000.0  # USD maps to USDT
    }
    
    with pytest.raises(ValueError, match="Currency XYZ not supported"):
        await fx_service.convert("USD", "XYZ", 1000.0)

@pytest.mark.asyncio
async def test_convert_invalid_rates(fx_service, mock_binance_service):
    mock_binance_service.get_btc_prices.return_value = {
        "BTCUSDT": 0.0,  # USD maps to USDT
        "BTCGBP": 35000.0
    }
    
    with pytest.raises(ValueError, match="Invalid exchange rates received"):
        await fx_service.convert("USD", "GBP", 1000.0)

@pytest.mark.asyncio
async def test_get_exchange_rate_same_currency(fx_service):
    result = await fx_service.get_exchange_rate("USD", "USD")
    assert result == 1.0

@pytest.mark.asyncio
async def test_get_exchange_rate_different_currencies(fx_service, mock_binance_service):
    mock_binance_service.get_btc_prices.return_value = {
        "BTCUSDT": 45000.0,  # USD maps to USDT
        "BTCGBP": 35000.0
    }
    
    result = await fx_service.get_exchange_rate("USD", "GBP")
    expected_rate = 45000.0 / 35000.0
    
    assert result == pytest.approx(expected_rate, rel=1e-6)

@pytest.mark.asyncio
async def test_get_supported_currencies(fx_service, mock_binance_service):
    expected_currencies = ["USD", "EUR", "GBP", "JPY"]
    mock_binance_service.get_supported_currencies.return_value = expected_currencies
    
    result = await fx_service.get_supported_currencies()
    
    assert result == expected_currencies
    mock_binance_service.get_supported_currencies.assert_called_once()