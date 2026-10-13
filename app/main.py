
from fastapi import FastAPI, HTTPException, Query

from app.schemas.batch import GenerateBatchRequest
from app.services.order_generator import generate_orders
from app.services.s3_storage import (
    upload_batch,
    list_batches,
    get_batch,
)

app = FastAPI(
    title="Data Source API",
    description="API for generating and serving raw ETL data.",
    version="1.0.0",
)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "data-source-api"}


@app.post("/api/v1/batches/generate", tags=["Batches"])
def create_batch(request: GenerateBatchRequest):
    # Genera el lote de datos sucios.
    batch = generate_orders(
        amount=request.amount,
        error_percentage=request.error_percentage,
        seed=request.seed,
    )

    # Guarda los datos y metadatos en S3.
    metadata = upload_batch(batch)

    # No devolvemos los 20.000 registros en esta respuesta.
    return {
        "status": "uploaded",
        **metadata,
    }


@app.get("/api/v1/batches", tags=["Batches"])
def read_batches(
    limit: int = Query(default=20, ge=1, le=100),
    continuation_token: str | None = None,
):
    return list_batches(
        limit=limit,
        continuation_token=continuation_token,
    )


@app.get("/api/v1/batches/{batch_id}", tags=["Batches"])
def read_batch(batch_id: str):
    batch = get_batch(batch_id)

    if batch is None:
        raise HTTPException(
            status_code=404,
            detail="Batch not found",
        )

    return batch
