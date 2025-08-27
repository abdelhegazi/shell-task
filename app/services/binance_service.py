import httpx
import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class BinanceService:
    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3"
        # Major global currencies for financial trading platforms
        self.supported_pairs = [
            # G7 Major Currencies
            "BTCUSDT",  # US Dollar - Global reserve currency
            "BTCEUR",  # Euro - European Union
            "BTCGBP",  # British Pound - UK financial markets
            "BTCJPY",  # Japanese Yen - Asian major currency
            "BTCCAD",  # Canadian Dollar - North American commodity currency
            # Additional Developed Market Currencies
            "BTCAUD",  # Australian Dollar - Asia-Pacific region
            "BTCCHF",  # Swiss Franc - Safe haven currency
            "BTCSEK",  # Swedish Krona - Nordic region
            "BTCNOK",  # Norwegian Krone - Oil-linked economy
            "BTCDKK",  # Danish Krone - EU-linked
            # Emerging Market Currencies (commonly traded)
            "BTCPLN",  # Polish Zloty - Central Europe
            "BTCZAR",  # South African Rand - Africa
            "BTCBRL",  # Brazilian Real - Latin America
            "BTCRUB",  # Russian Ruble - Eastern Europe/Asia
            "BTCINR",  # Indian Rupee - South Asia
            "BTCKRW",  # Korean Won - Asia
            "BTCMXN",  # Mexican Peso - North America
            "BTCTRY",  # Turkish Lira - Europe/Asia bridge
        ]
        self._client = None
        self._last_fetch = None
        self._cached_rates = {}

        # Cache for supported pairs validation (fetched from Binance)
        self._validated_pairs = None
        self._pairs_last_validated = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=30.0,
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
            )
        return self._client

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    async def get_btc_prices(self, force_refresh: bool = False) -> Dict[str, float]:
        now = datetime.utcnow()

        if (
            not force_refresh
            and self._last_fetch
            and self._cached_rates
            and now - self._last_fetch < timedelta(hours=1)
        ):
            logger.info("Using cached BTC rates")
            return self._cached_rates

        try:
            client = await self._get_client()

            # Use validated pairs instead of hardcoded list
            validated_pairs = await self.validate_supported_pairs()

            tasks = []
            for pair in validated_pairs:
                task = self._fetch_single_price(client, pair)
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)

            rates = {}
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.warning(f"Failed to fetch {validated_pairs[i]}: {result}")
                    continue

                symbol, price = result
                if price is not None:
                    rates[symbol] = price

            if not rates:
                raise ValueError("No BTC rates could be fetched from Binance")

            self._cached_rates = rates
            self._last_fetch = now
            logger.info(f"Fetched {len(rates)} BTC rates from Binance")

            return rates

        except Exception as e:
            logger.error(f"Error fetching BTC prices: {str(e)}")
            if self._cached_rates:
                logger.info("Falling back to cached rates")
                return self._cached_rates
            raise

    async def _fetch_single_price(
        self, client: httpx.AsyncClient, symbol: str
    ) -> tuple[str, Optional[float]]:
        try:
            response = await client.get(
                f"{self.base_url}/ticker/price", params={"symbol": symbol}
            )
            response.raise_for_status()

            data = response.json()
            price = float(data["price"])
            return symbol, price

        except Exception as e:
            logger.warning(f"Failed to fetch {symbol}: {str(e)}")
            return symbol, None

    def get_currency_from_pair(self, pair: str) -> str:
        if pair.startswith("BTC") and len(pair) >= 6:
            currency = pair[3:]
            # Map USDT to USD for user-friendly API
            if currency == "USDT":
                return "USD"
            return currency
        return ""

    async def validate_supported_pairs(self) -> List[str]:
        """Validate which pairs are actually available on Binance and cache the result."""
        now = datetime.utcnow()

        # Use cached validation if less than 24 hours old
        if (
            self._validated_pairs is not None
            and self._pairs_last_validated
            and now - self._pairs_last_validated < timedelta(hours=24)
        ):
            return self._validated_pairs

        try:
            client = await self._get_client()
            # Get all available symbols from Binance
            response = await client.get(f"{self.base_url}/exchangeInfo")
            response.raise_for_status()

            exchange_info = response.json()
            available_symbols = {
                symbol["symbol"]
                for symbol in exchange_info["symbols"]
                if symbol["status"] == "TRADING"
            }

            # Filter our supported pairs against what's actually available
            validated_pairs = [
                pair for pair in self.supported_pairs if pair in available_symbols
            ]

            self._validated_pairs = validated_pairs
            self._pairs_last_validated = now

            logger.info(
                f"Validated {len(validated_pairs)} BTC pairs out of {len(self.supported_pairs)} requested"
            )

            return validated_pairs

        except Exception as e:
            logger.error(f"Error validating supported pairs: {str(e)}")
            # Fallback to our predefined list if validation fails
            return self.supported_pairs

    async def get_supported_currencies(self) -> List[str]:
        """Get list of supported currencies based on validated trading pairs."""
        validated_pairs = await self.validate_supported_pairs()
        currencies = []
        for pair in validated_pairs:
            currency = self.get_currency_from_pair(pair)
            if currency:
                currencies.append(currency)
        return sorted(list(set(currencies)))
