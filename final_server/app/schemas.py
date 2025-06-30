from pydantic import BaseModel, ConfigDict
from datetime import datetime


class SensorReadingBase(BaseModel):
    sensor_id: int
    timestamp: datetime
    temperature: float
    pressure: float
    humidity: float

class SensorReadingCreate(SensorReadingBase):
    pass

class SensorReading(SensorReadingBase):
    id: int

    model_config = ConfigDict(from_attributes=True)