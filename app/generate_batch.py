
import json
import os

from app.services.order_generator import generate_orders
from app.services.s3_storage import upload_batch


def main():
    amount = int(os.getenv("BATCH_SIZE", "20000"))
    error_percentage = float(os.getenv("ERROR_PERCENTAGE", "20"))

    seed_value = os.getenv("BATCH_SEED")
    seed = int(seed_value) if seed_value is not None else None

    batch = generate_orders(
        amount=amount,
        error_percentage=error_percentage,
        seed=seed,
    )

    metadata = upload_batch(batch)

    print(json.dumps({
        "status": "uploaded",
        **metadata,
    }))


if __name__ == "__main__":
    main()
