from fastapi import FastAPI

app = FastAPI(
    title="Parkolóhely-foglalás API",
    description="Backend szolgáltatás parkolóhelyek kezeléséhez és foglalásához.",
    version="1.0.0"
)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "A Parkolóhely-foglalás API fut!"}