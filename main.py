from src.data import DB8583

with DB8583() as db:
    db.iso_db(file_date="26/05/2026", cycle="CIC1")
    db.iso_db(file_date="26/05/2025", cycle="CIC2")
    db.iso_db(file_date="26/05/2025", cycle="CIC3")
