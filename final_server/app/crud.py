# Database operations (Create, Read, Update, Delete)

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

def create_reading(db:Session, reading: schemas.SensorReadingCreate):
    db_reading = models.SensorReadings(**reading.model_dump())
    db.add(db_reading)
    db.commit()
    db.refresh(db_reading)
    return db_reading