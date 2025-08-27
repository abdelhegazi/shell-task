import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Query

from app.models.response import ConversionResponse
from app.services.binance_service import BinanceService
from app.services.fx_service import FXService
from app.utils.cache import CacheManager

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Currency Converter API")
    yield
    logger.info("Shutting down Currency Converter API")


app = FastAPI(
    title="Currency Converter API",
    description="Real-time currency conversion using Binance BTC rates",
    version="1.0.0",
    lifespan=lifespan,
)

binance_service = BinanceService()
fx_service = FXService(binance_service)
cache_manager = CacheManager()


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "currency-converter"}


@app.get("/convert", response_model=ConversionResponse)
async def convert_currency(
    ccy_from: str = Query(..., description="Source currency code (e.g., USD)"),
    ccy_to: str = Query(..., description="Target currency code (e.g., GBP)"),
    quantity: float = Query(..., gt=0, description="Amount to convert"),
):
    try:
        converted_amount = await fx_service.convert(
            from_currency=ccy_from.upper(), to_currency=ccy_to.upper(), amount=quantity
        )

        return ConversionResponse(
            quantity=round(converted_amount, 2), ccy=ccy_to.upper()
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Conversion error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
