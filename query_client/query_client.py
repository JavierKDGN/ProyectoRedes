import asyncio
import aiohttp
from pydantic import ValidationError

from final_server.app.schemas import SensorReadingCreate

TEMP_RANGE = (0,30)
HUMI_RANGE = (40,70)
PRES_RANGE = (980,1020)

def validar_limites(reading: SensorReadingCreate):
    temp_ok = TEMP_RANGE[0] <= reading.temperature <= TEMP_RANGE[1]
    humi_ok = HUMI_RANGE[0] <= reading.humidity <= HUMI_RANGE[1]
    pres_ok = PRES_RANGE[0] <= reading.pressure <= PRES_RANGE[1]

    checks = [temp_ok, humi_ok, pres_ok]

    if not all(checks):
        if not temp_ok:
            print(f"Temperatura fuera de rango: {reading.temperature} C")
            print(f"Rango permitido: {TEMP_RANGE[0]} - {TEMP_RANGE[1]} C")
        if not humi_ok:
            print(f"Humedad fuera de rango: {reading.humidity} %")
            print(f"Rango permitido: {HUMI_RANGE[0]} - {HUMI_RANGE[1]} %")
        if not pres_ok:
            print(f"Presion fuera de rango: {reading.pressure} hPa")
            print(f"Rango permitido: {PRES_RANGE[0]} - {PRES_RANGE[1]} hPa")

# Funcion asincrona para pedir data de un url usando aiohttp
async def fetch_data(session, url):

    async with session.get(url) as response:
        try:
            data = await response.json()
            if isinstance(data, list):
                readings = [SensorReadingCreate.model_validate(item) for item in data]
                return readings
            reading = [SensorReadingCreate.model_validate(data)]
            return reading
        except ValidationError as e:
            print(f"Error de validacion de datos: {e}")
            return None


# Main asincrono
async def main():
    # URL del servidor
    url = "http://localhost:8000/readings/?skip=0&limit=10"
    max_retries = 5
    # Crear una sesion aiohttp para hacer requests asincronas
    async with aiohttp.ClientSession() as session:
        # Recibe datos cada 5 segundos
        while True:
            retries = 0
            while retries < max_retries:
                try:
                    readings = await fetch_data(session, url)
                    if readings is not None:
                        for read in readings:
                            print(read)
                            validar_limites(read)
                            print("------------------------------------")
                    break
                except aiohttp.ClientError as e:
                    print(f"Request fallida: '{e}'. Reintentando..")
                    retries += 1
                    backoff = 2
                    await asyncio.sleep(backoff)

            else:
                print("Intentos maximos alcanzados. Saltando iteracion")
            await asyncio.sleep(5)



if __name__ == "__main__":
    asyncio.run(main())
