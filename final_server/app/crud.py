# Database operations (Create, Read, Update, Delete)
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from . import models, schemas

def get_readings(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.SensorReadings)\
        .order_by(models.SensorReadings.timestamp.desc())\
        .offset(skip)\
        .limit(limit).all()

def get_readings_by_sensor_id(db: Session, sensor_id: int):
    return db.query(models.SensorReadings)\
        .filter(models.SensorReadings.sensor_id == sensor_id)\
        .order_by(models.SensorReadings.timestamp.desc())\
        .all()

def get_filtered_readings(db: Session,
                          skip: int,
                          limit: int,
                          sensor_id: Optional[int] = None,
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None,
                          min_temp: Optional[float] = None,
                          max_temp: Optional[float] = None,
                          min_pres: Optional[float] = None,
                          max_pres: Optional[float] = None,
                          min_humi: Optional[float] = None,
                          max_humi: Optional[float] = None):
    query = db.query(models.SensorReadings)

    if sensor_id is not None:
        query = query.filter(models.SensorReadings.sensor_id == sensor_id)
    if start_date is not None:
        query = query.filter(models.SensorReadings.timestamp >= start_date)
    if end_date is not None:
        query = query.filter(models.SensorReadings.timestamp <= end_date)
    if min_temp is not None:
        query = query.filter(models.SensorReadings.temperature >= min_temp)
    if max_temp is not None:
        query = query.filter(models.SensorReadings.temperature <= max_temp)
    if min_pres is not None:
        query = query.filter(models.SensorReadings.pressure >= min_pres)
    if max_pres is not None:
        query = query.filter(models.SensorReadings.pressure <= max_pres)
    if min_humi is not None:
        query = query.filter(models.SensorReadings.humidity >= min_humi)
    if max_humi is not None:
        query = query.filter(models.SensorReadings.humidity <= max_humi)

    return query.order_by(models.SensorReadings.timestamp.desc()).offset(skip).limit(limit).all()

def create_reading(db:Session, reading: schemas.SensorReadingCreate):
    db_reading = models.SensorReadings(**reading.model_dump())
    db.add(db_reading)
    db.commit()
    db.refresh(db_reading)
    return db_reading