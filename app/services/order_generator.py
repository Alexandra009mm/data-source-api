
import random
import uuid
from datetime import date, timedelta


CITIES = [
    "Barranquilla",
    "Bogota",
    "Medellin",
    "Cali",
]

PRODUCTS = [
    ("Teclado", "85000"),
    ("Mouse", "45000"),
    ("Monitor", "780000"),
]


def generate_orders(
    amount: int,
    error_percentage: float,
    seed: int | None = None,
) -> dict:
    rng = random.Random(seed)

    # Cada lote tiene un identificador único.
    batch_id = str(uuid.uuid4())

    orders = []
    dirty_count = round(amount * error_percentage / 100)

    start_date = date(2026, 9, 1)

    for index in range(amount):
        order_date = start_date + timedelta(days=index % 30)
        product, price = rng.choice(PRODUCTS)

        order = {
            "order_id": str(1001 + index),
            "order_date": order_date.isoformat(),
            "customer_id": f"C{rng.randint(1, 100):03d}",
            "city": rng.choice(CITIES),
            "product": product,
            "quantity": str(rng.randint(1, 5)),
            "unit_price": price,
        }

        orders.append(order)

    # Elegimos qué registros tendrán errores.
    dirty_indexes = rng.sample(range(amount), dirty_count)

    error_types = [
        "invalid_date",
        "invalid_city",
        "negative_quantity",
        "missing_value",
        "negative_price",
    ]

    for index in dirty_indexes:
        order = orders[index]
        error_type = rng.choice(error_types)

        if error_type == "invalid_date":
            order["order_date"] = "2026-99-45"

        elif error_type == "invalid_city":
            order["city"] = rng.choice([
                "barranquilla",
                "BOGOTÁ",
                "Medellin ",
                "bogotaa",
            ])

        elif error_type == "negative_quantity":
            order["quantity"] = "-2"

        elif error_type == "missing_value":
            field = rng.choice([
                "customer_id",
                "city",
                "product",
            ])
            order[field] = None

        elif error_type == "negative_price":
            order["unit_price"] = "-85000"

    return {
        "batch_id": batch_id,
        "total_records": len(orders),
        "dirty_records": dirty_count,
        "orders": orders,
    }
