#!/usr/bin/env python3
"""
Script to populate the database with dummy sensor data for testing purposes.
"""

import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models, schemas

def create_dummy_data():
    """
    Creates dummy sensor readings for testing.
    Generates data for 5 different sensors over the last 30 days.
    """
    # Create database tables
    models.Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Clear existing data (optional - remove if you want to keep existing data)
        db.query(models.SensorReadings).delete()
        db.commit()

        # Configuration for dummy data
        num_sensors = 5
        days_back = 30
        readings_per_day = 24  # One reading per hour

        print(f"Generating dummy data for {num_sensors} sensors over {days_back} days...")

        # Generate readings for each sensor
        for sensor_id in range(1, num_sensors + 1):
            print(f"Generating data for sensor {sensor_id}...")

            # Base values for this sensor (each sensor has slightly different ranges)
            base_temp = 20 + (sensor_id * 2)  # 22, 24, 26, 28, 30
            base_pressure = 1000 + (sensor_id * 5)  # 1005, 1010, 1015, 1020, 1025
            base_humidity = 40 + (sensor_id * 8)  # 48, 56, 64, 72, 80

            # Generate readings for the last 'days_back' days
            for day in range(days_back):
                date = datetime.now() - timedelta(days=day)

                for hour in range(0, 24, 24 // readings_per_day):
                    timestamp = date.replace(hour=hour, minute=random.randint(0, 59), second=random.randint(0, 59))

                    # Add some realistic variation to the values
                    temperature = base_temp + random.uniform(-5, 5)
                    pressure = base_pressure + random.uniform(-20, 20)
                    humidity = max(0, min(100, base_humidity + random.uniform(-15, 15)))

                    # Create reading
                    reading_data = schemas.SensorReadingCreate(
                        sensor_id=sensor_id,
                        timestamp=timestamp,
                        temperature=round(temperature, 2),
                        pressure=round(pressure, 2),
                        humidity=round(humidity, 2)
                    )

                    db_reading = models.SensorReadings(**reading_data.model_dump())
                    db.add(db_reading)

            # Commit after each sensor to avoid memory issues
            db.commit()

        # Count total readings
        total_readings = db.query(models.SensorReadings).count()
        print(f"Successfully created {total_readings} dummy sensor readings!")

        # Show some sample data
        print("\nSample data (latest 5 readings):")
        latest_readings = db.query(models.SensorReadings)\
            .order_by(models.SensorReadings.timestamp.desc())\
            .limit(5).all()

        for reading in latest_readings:
            print(f"Sensor {reading.sensor_id}: {reading.timestamp} - "
                  f"Temp: {reading.temperature}°C, "
                  f"Pressure: {reading.pressure}hPa, "
                  f"Humidity: {reading.humidity}%")

    except Exception as e:
        print(f"Error creating dummy data: {e}")
        db.rollback()
    finally:
        db.close()

def show_data_summary():
    """
    Shows a summary of the current data in the database.
    """
    db = SessionLocal()
    try:
        total_readings = db.query(models.SensorReadings).count()
        if total_readings == 0:
            print("No sensor readings found in database.")
            return

        print(f"\nDatabase Summary:")
        print(f"Total readings: {total_readings}")

        # Get unique sensor IDs
        sensor_ids = db.query(models.SensorReadings.sensor_id).distinct().all()
        sensor_ids = [sid[0] for sid in sensor_ids]
        print(f"Sensors: {sorted(sensor_ids)}")

        # Get date range
        oldest = db.query(models.SensorReadings).order_by(models.SensorReadings.timestamp.asc()).first()
        newest = db.query(models.SensorReadings).order_by(models.SensorReadings.timestamp.desc()).first()

        if oldest and newest:
            print(f"Date range: {oldest.timestamp.date()} to {newest.timestamp.date()}")

        # Show readings per sensor
        print("\nReadings per sensor:")
        for sensor_id in sorted(sensor_ids):
            count = db.query(models.SensorReadings)\
                .filter(models.SensorReadings.sensor_id == sensor_id)\
                .count()
            print(f"  Sensor {sensor_id}: {count} readings")

    except Exception as e:
        print(f"Error showing summary: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--summary":
        show_data_summary()
    else:
        print("Creating dummy sensor data...")
        create_dummy_data()
        print("\nTo see a summary of the data, run:")
        print("python populate_dummy_data.py --summary")
