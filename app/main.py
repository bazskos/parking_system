from fastapi import FastAPI
from .database import engine, SessionLocal
from . import models

# 1. Létrehozzuk a táblákat az adatbázisban a models.py alapján
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Parkolóhely-foglalás API",
    description="Backend szolgáltatás parkolóhelyek kezeléséhez és foglalásához.",
    version="1.0.0"
)

def init_db():
    # Nyitunk egy adatbázis munkamenetet (session)
    db = SessionLocal()
    try:
        # 2. Megnézzük, van-e már adat a ParkingSpot táblában
        if db.query(models.ParkingSpot).count() == 0:
            # Ha nincs, létrehozunk 5 alapértelmezett parkolóhelyet
            alap_helyek = [
                models.ParkingSpot(name="P-01", type="normal"),
                models.ParkingSpot(name="P-02", type="normal"),
                models.ParkingSpot(name="P-03", type="normal"),
                models.ParkingSpot(name="VIP-01", type="vip"),
                models.ParkingSpot(name="DIS-01", type="disabled"),
            ]
            db.add_all(alap_helyek)
            db.commit()
            print("Adatbázis sikeresen feltöltve alap adatokkal!")
    finally:
        db.close()

# 3. Meghívjuk az inicializáló függvényt az app indulásakor 
init_db()

@app.get("/")
def health_check():
    return {"status": "ok", "message": "A Parkolóhely-foglalás API fut és az adatbázis inicializálva!"}