import os
import pandas as pd
from typing import Optional, Dict, Any
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import crud, models, schemas
from .database import SessionLocal, engine

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
models.Base.metadata.create_all(bind=engine)
app = FastAPI()
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open(os.path.join(STATIC_DIR, "index.html"), encoding='utf-8') as f:
        return HTMLResponse(content=f.read(), status_code=200)

@app.post("/readings/", response_model=schemas.SensorReading)
def create_reading(reading: schemas.SensorReadingCreate, db: Session = Depends(get_db)):
    return crud.create_reading(db=db, reading=reading)

@app.get("/readings/", response_model=list[schemas.SensorReading])
def read_readings(skip: int = 0,
                  limit: int = 100,
                  sensor_id: Optional[int] = None,
                  start_date: Optional[datetime] = None,
                  end_date: Optional[datetime] = None,
                  min_temp: Optional[float] = None,
                  max_temp: Optional[float] = None,
                  min_pres: Optional[float] = None,
                  max_pres: Optional[float] = None,
                  min_humi: Optional[float] = None,
                  max_humi: Optional[float] = None,
                  db: Session = Depends(get_db)):
    readings = crud.get_filtered_readings(db, skip = skip, limit = limit,
                                          sensor_id = sensor_id,
                                          start_date = start_date,
                                          end_date = end_date,
                                          min_temp = min_temp,
                                          max_temp = max_temp,
                                          min_pres = min_pres,
                                          max_pres = max_pres,
                                          min_humi = min_humi,
                                          max_humi = max_humi)
    return readings

@app.get("/readings/stats/", response_model=Dict[str, Any])
def get_reading_stats(sensor_id: Optional[int] = None,
                  start_date: Optional[datetime] = None,
                  end_date: Optional[datetime] = None,
                  min_temp: Optional[float] = None,
                  max_temp: Optional[float] = None,
                  min_pres: Optional[float] = None,
                  max_pres: Optional[float] = None,
                  min_humi: Optional[float] = None,
                  max_humi: Optional[float] = None,
                  db: Session = Depends(get_db)):

    readings = crud.get_filtered_readings(db, skip = 0, limit = 10000,
                                          sensor_id = sensor_id,
                                          start_date = start_date,
                                          end_date = end_date,
                                          min_temp = min_temp,
                                          max_temp = max_temp,
                                          min_pres = min_pres,
                                          max_pres = max_pres,
                                          min_humi = min_humi,
                                          max_humi = max_humi)

    df = pd.DataFrame([reading.__dict__ for reading in readings])
    df = df.drop(columns=['_sa_instance_state'], errors='ignore')
    number_col = ['temperature', 'pressure', 'humidity']
    df_num = df[number_col]
    stats_df = df_num.describe()
    stats = {
        'count': len(df),
        'stats': stats_df.to_dict()
    }

    return stats





