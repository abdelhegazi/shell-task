import httpx
import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class BinanceService:
    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3"
        self.supported_pairs = [
            "BTCUSDT", "BTCEUR", "BTCGBP", "BTCJPY", 
            "BTCAUD", "BTCCAD", "BTCCHF", "BTCSEK",
            "BTCNOK", "BTCDKK", "BTCPLN", "BTCZAR"
        ]
        self._client = None
        self._last_fetch = None
        self._cached_rates = {}

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=30.0,
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
            )
        return self._client

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    async def get_btc_prices(self, force_refresh: bool = False) -> Dict[str, float]:
        now = datetime.utcnow()
        
        if (not force_refresh and 
            self._last_fetch and 
            self._cached_rates and 
            now - self._last_fetch < timedelta(hours=1)):
            logger.info("Using cached BTC rates")
            return self._cached_rates

        try:
            client = await self._get_client()
            
            tasks = []
            for pair in self.supported_pairs:
                task = self._fetch_single_price(client, pair)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            rates = {}
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.warning(f"Failed to fetch {self.supported_pairs[i]}: {result}")
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

    async def _fetch_single_price(self, client: httpx.AsyncClient, symbol: str) -> tuple[str, Optional[float]]:
        try:
            response = await client.get(f"{self.base_url}/ticker/price", params={"symbol": symbol})
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

    async def get_supported_currencies(self) -> List[str]:
        currencies = []
        for pair in self.supported_pairs:
            currency = self.get_currency_from_pair(pair)
            if currency:
                currencies.append(currency)
        return sorted(list(set(currencies)))