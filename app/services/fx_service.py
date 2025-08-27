import logging
from typing import Dict
from app.services.binance_service import BinanceService

logger = logging.getLogger(__name__)

class FXService:
    def __init__(self, binance_service: BinanceService):
        self.binance_service = binance_service

    def _get_btc_pair_for_currency(self, currency: str) -> str:
        # Map USD to USDT for Binance API
        if currency == "USD":
            return "BTCUSDT"
        return f"BTC{currency}"

    async def convert(self, from_currency: str, to_currency: str, amount: float) -> float:
        if amount <= 0:
            raise ValueError("Amount must be greater than 0")

        if from_currency == to_currency:
            return amount

        btc_rates = await self.binance_service.get_btc_prices()
        
        from_btc_pair = self._get_btc_pair_for_currency(from_currency)
        to_btc_pair = self._get_btc_pair_for_currency(to_currency)

        if from_btc_pair not in btc_rates:
            raise ValueError(f"Currency {from_currency} not supported")
        
        if to_btc_pair not in btc_rates:
            raise ValueError(f"Currency {to_currency} not supported")

        from_btc_rate = btc_rates[from_btc_pair]
        to_btc_rate = btc_rates[to_btc_pair]

        if from_btc_rate <= 0 or to_btc_rate <= 0:
            raise ValueError("Invalid exchange rates received")

        exchange_rate = from_btc_rate / to_btc_rate
        converted_amount = amount * exchange_rate

        logger.info(
            f"Converted {amount} {from_currency} to {converted_amount:.4f} {to_currency} "
            f"(rate: {exchange_rate:.6f})"
        )

        return converted_amount

    async def get_exchange_rate(self, from_currency: str, to_currency: str) -> float:
        if from_currency == to_currency:
            return 1.0

        btc_rates = await self.binance_service.get_btc_prices()
        
        from_btc_pair = self._get_btc_pair_for_currency(from_currency)
        to_btc_pair = self._get_btc_pair_for_currency(to_currency)

        if from_btc_pair not in btc_rates:
            raise ValueError(f"Currency {from_currency} not supported")
        
        if to_btc_pair not in btc_rates:
            raise ValueError(f"Currency {to_currency} not supported")

        from_btc_rate = btc_rates[from_btc_pair]
        to_btc_rate = btc_rates[to_btc_pair]

        return from_btc_rate / to_btc_rate

    async def get_supported_currencies(self) -> list[str]:
        return await self.binance_service.get_supported_currencies()