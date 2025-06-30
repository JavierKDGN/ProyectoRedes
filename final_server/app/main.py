from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/readings/", response_model=schemas.SensorReading)
def create_reading(reading: schemas.SensorReadingCreate, db: Session = Depends(get_db)):
    return crud.create_reading(db=db, reading=reading)

@app.get("/readings/", response_model=list[schemas.SensorReading])
def read_readings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    readings = crud.get_readings(db, skip = skip, limit = limit)
    return readings
