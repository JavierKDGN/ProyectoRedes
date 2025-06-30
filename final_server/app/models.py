# SQLAlchemy data

from sqlalchemy import Boolean, Column, DateTime, Integer, Float

from .database import Base


class SensorReadings(Base):
    """
    Representa una unica lectura de un sensor almacenada en la tabla 'sensor_readings'.

    Esta clase es un modelo ORM de SQLAlchemy que mapea los objetos de Python
    a las filas de la tabla de la base de datos.

    Atributos:
        id (Integer): Primary key auto-incremental.
        sensor_id (Integer): Identificador del sensor que origino la lectura.
        timestamp (DateTime): Fecha y hora de la lectura. [yyyy-mm-dd]
        temperature (Float): Valor de la temperatura.
        pressure (Float): Valor de la presion.
        humidity (Float): Valor de la humedad.
    """
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True)
    sensor_id = Column(Integer, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    temperature = Column(Float, nullable=False)
    pressure = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
