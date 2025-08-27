from unittest.mock import patch

import httpx
import pytest

from app.services.binance_service import BinanceService


@pytest.fixture
def binance_service():
    return BinanceService()


@pytest.mark.asyncio
async def test_get_btc_prices_success(binance_service):
    mock_response_data = {"symbol": "BTCUSDT", "price": "45000.00"}

    class MockResponse:
        def json(self):
            return mock_response_data

        async def raise_for_status(self):
            pass

    async def mock_get_response(*args, **kwargs):
        return MockResponse()

    with patch.object(httpx.AsyncClient, "get", side_effect=mock_get_response):
        # Mock the validate_supported_pairs method
        with patch.object(
            binance_service, "validate_supported_pairs", return_value=["BTCUSDT"]
        ):
            rates = await binance_service.get_btc_prices(force_refresh=True)

            assert "BTCUSDT" in rates
            assert rates["BTCUSDT"] == 45000.00


@pytest.mark.asyncio
async def test_get_btc_prices_cached(binance_service):
    from datetime import datetime

    binance_service._cached_rates = {"BTCUSDT": 45000.00}
    binance_service._last_fetch = datetime.utcnow()

    rates = await binance_service.get_btc_prices()

    assert "BTCUSDT" in rates
    assert rates["BTCUSDT"] == 45000.00


@pytest.mark.asyncio
async def test_fetch_single_price_success(binance_service):
    mock_response_data = {"symbol": "BTCUSDT", "price": "45000.00"}

    class MockResponse:
        def json(self):
            return mock_response_data

        async def raise_for_status(self):
            pass

    async def mock_get_response(*args, **kwargs):
        return MockResponse()

    with patch.object(httpx.AsyncClient, "get", side_effect=mock_get_response):
        client = await binance_service._get_client()
        symbol, price = await binance_service._fetch_single_price(client, "BTCUSDT")

        assert symbol == "BTCUSDT"
        assert price == 45000.00


@pytest.mark.asyncio
async def test_fetch_single_price_failure(binance_service):
    with patch.object(httpx.AsyncClient, "get") as mock_get:
        mock_get.side_effect = httpx.RequestError("Connection error")

        client = await binance_service._get_client()
        symbol, price = await binance_service._fetch_single_price(client, "BTCUSDT")

        assert symbol == "BTCUSDT"
        assert price is None


def test_get_currency_from_pair(binance_service):
    assert (
        binance_service.get_currency_from_pair("BTCUSDT") == "USD"
    )  # USDT maps to USD
    assert binance_service.get_currency_from_pair("BTCEUR") == "EUR"
    assert binance_service.get_currency_from_pair("BTCGBP") == "GBP"
    assert binance_service.get_currency_from_pair("INVALID") == ""


@pytest.mark.asyncio
async def test_get_supported_currencies(binance_service):
    # Mock validate_supported_pairs to return a subset of pairs
    mock_pairs = ["BTCUSDT", "BTCEUR", "BTCGBP", "BTCJPY"]
    with patch.object(
        binance_service, "validate_supported_pairs", return_value=mock_pairs
    ):
        currencies = await binance_service.get_supported_currencies()

        expected_currencies = ["USD", "EUR", "GBP", "JPY"]  # USDT maps to USD

        assert set(currencies) == set(expected_currencies)


@pytest.mark.asyncio
async def test_close_client(binance_service):
    """Test closing the HTTP client."""
    # Create a client first
    await binance_service._get_client()
    assert binance_service._client is not None

    # Close the client
    await binance_service.close()
    assert binance_service._client is None


@pytest.mark.asyncio
async def test_close_client_when_none(binance_service):
    """Test closing when client is None."""
    # Ensure client is None
    binance_service._client = None

    # This should not raise an error
    await binance_service.close()
    assert binance_service._client is None


@pytest.mark.asyncio
async def test_get_btc_prices_fallback_to_cache(binance_service):
    """Test fallback to cached rates when API fails."""
    # Set up cached rates
    cached_rates = {"BTCUSDT": 45000.0, "BTCEUR": 37500.0}
    binance_service._cached_rates = cached_rates

    # Mock validate_supported_pairs to fail
    with patch.object(
        binance_service, "validate_supported_pairs", side_effect=Exception("API Error")
    ):
        rates = await binance_service.get_btc_prices(force_refresh=True)
        assert rates == cached_rates


@pytest.mark.asyncio
async def test_get_btc_prices_no_cache_fallback(binance_service):
    """Test error when no cached rates available."""
    # Ensure no cached rates
    binance_service._cached_rates = {}

    # Mock validate_supported_pairs to fail
    with patch.object(
        binance_service, "validate_supported_pairs", side_effect=Exception("API Error")
    ):
        with pytest.raises(Exception, match="API Error"):
            await binance_service.get_btc_prices(force_refresh=True)


@pytest.mark.asyncio
async def test_validate_supported_pairs_exception_fallback(binance_service):
    """Test validate_supported_pairs fallback to predefined list on error."""

    class MockResponse:
        def json(self):
            raise Exception("JSON parsing error")

        async def raise_for_status(self):
            pass

    async def mock_get_response(*args, **kwargs):
        return MockResponse()

    with patch.object(httpx.AsyncClient, "get", side_effect=mock_get_response):
        pairs = await binance_service.validate_supported_pairs()
        # Should return the predefined supported_pairs list as fallback
        assert pairs == binance_service.supported_pairs


@pytest.mark.asyncio
async def test_validate_supported_pairs_cached(binance_service):
    """Test validate_supported_pairs using cached validation."""
    from datetime import datetime

    # Set up cached validation
    expected_pairs = ["BTCUSDT", "BTCEUR"]
    binance_service._validated_pairs = expected_pairs
    binance_service._pairs_last_validated = datetime.utcnow()

    pairs = await binance_service.validate_supported_pairs()
    assert pairs == expected_pairs
