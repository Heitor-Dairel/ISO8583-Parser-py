from src.data import DB8583

with DB8583() as db:
    db.iso_db(file_date="05/02/2026", file_cycle="CIC2")
