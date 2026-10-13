
from pydantic import BaseModel, Field


class GenerateBatchRequest(BaseModel):
    # Cantidad de registros que se generarán en el lote
    amount: int = Field(default=20000, ge=1, le=20000)

    # Porcentaje de registros que tendrán datos sucios
    error_percentage: float = Field(default=20, ge=0, le=100)

    # Permite repetir los mismos datos cuando se proporciona una semilla
    seed: int | None = None
