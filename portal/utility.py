from .models import SparePart

def get_sparepart_data():
    rows = SparePart.objects.values(
        "stock_code",
        "description",
        "price_usd",
        "price_eur",
        "price_gbp",
        "price_try",
    )
    data = {}
    for row in rows:
        stock_code = row["stock_code"]

        inner = {}
        for key, value in row.items():
            if key != "stock_code":
                inner[key] = f"{value}"
        data[stock_code] = inner
    return data