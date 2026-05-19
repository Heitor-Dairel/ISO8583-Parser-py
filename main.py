from src.data import DB8583

with DB8583() as db:
    db.iso_db(date_file="24/12/2025", cycle="CIC1")
