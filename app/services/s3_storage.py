
import json
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError

from app.core.config import settings


def get_s3_client():
    return boto3.client(
        "s3",
        region_name=settings.aws_default_region,
    )


def upload_batch(batch: dict) -> dict:
    """Guarda los registros y los metadatos de un lote en S3."""
    s3 = get_s3_client()
    bucket = settings.s3_bucket

    now = datetime.now(timezone.utc)
    batch_id = batch["batch_id"]

    # Cada línea del archivo representa un registro.
    content = "\n".join(
        json.dumps(order, ensure_ascii=False)
        for order in batch["orders"]
    ) + "\n"

    data_key = (
        f"raw/orders/year={now:%Y}/month={now:%m}/"
        f"day={now:%d}/{batch_id}.jsonl"
    )
    metadata_key = f"raw/metadata/{batch_id}.json"

    metadata = {
        "batch_id": batch_id,
        "total_records": batch["total_records"],
        "dirty_records": batch["dirty_records"],
        "data_key": data_key,
        "created_at": now.isoformat(),
    }

    # Primero guardamos los registros crudos.
    s3.put_object(
        Bucket=bucket,
        Key=data_key,
        Body=content.encode("utf-8"),
        ContentType="application/x-ndjson",
    )

    # Después guardamos los metadatos del lote.
    s3.put_object(
        Bucket=bucket,
        Key=metadata_key,
        Body=json.dumps(metadata, ensure_ascii=False).encode("utf-8"),
        ContentType="application/json",
    )

    return metadata


def list_batches(limit: int = 20, continuation_token: str | None = None) -> dict:
    """Lista los lotes guardados en S3 con paginación."""
    s3 = get_s3_client()

    params = {
        "Bucket": settings.s3_bucket,
        "Prefix": "raw/metadata/",
        "MaxKeys": limit,
    }

    if continuation_token:
        params["ContinuationToken"] = continuation_token

    response = s3.list_objects_v2(**params)
    batches = []

    for item in response.get("Contents", []):
        result = s3.get_object(
            Bucket=settings.s3_bucket,
            Key=item["Key"],
        )
        metadata = json.loads(result["Body"].read().decode("utf-8"))
        batches.append(metadata)

    return {
        "batches": batches,
        "next_token": response.get("NextContinuationToken"),
    }


def get_batch(batch_id: str) -> dict | None:
    """Recupera los metadatos y registros crudos de un lote."""
    s3 = get_s3_client()
    bucket = settings.s3_bucket
    metadata_key = f"raw/metadata/{batch_id}.json"

    try:
        metadata_response = s3.get_object(
            Bucket=bucket,
            Key=metadata_key,
        )
    except ClientError as error:
        code = error.response.get("Error", {}).get("Code")
        if code in ("NoSuchKey", "404", "NotFound"):
            return None
        raise

    metadata = json.loads(
        metadata_response["Body"].read().decode("utf-8")
    )

    data_response = s3.get_object(
        Bucket=bucket,
        Key=metadata["data_key"],
    )

    content = data_response["Body"].read().decode("utf-8")
    orders = [
        json.loads(line)
        for line in content.splitlines()
        if line.strip()
    ]

    return {
        **metadata,
        "orders": orders,
    }
