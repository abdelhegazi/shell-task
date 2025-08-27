from pydantic import BaseModel

class ConversionResponse(BaseModel):
    quantity: float
    ccy: str