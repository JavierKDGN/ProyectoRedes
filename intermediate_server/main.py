import socketserver
import struct
import hmac
import hashlib
import json
import requests
from datetime import datetime, timezone

# --- CONFIGURACIÓN DEL SERVIDOR ---
# Dirección y puerto donde este servidor escuchará las conexiones TCP del sensor C++
LISTEN_HOST = "0.0.0.0"  # Escuchar en todas las interfaces de red disponibles
LISTEN_PORT = 8080

# URL del Servidor Final (FastAPI) al que se reenviarán los datos
FINAL_SERVER_URL = "http://localhost:8000/readings/"

# Clave secreta compartida para la verificación HMAC. DEBE ser la misma que en el cliente C++.
HMAC_KEY = b"my-super-secret-key-for-dev"

# Definición del formato del paquete binario y su tamaño.
# Corresponde a la struct de C++: <h Q f f f 32s>
# '<' -> Little-endian
# 'h' -> short (2 bytes, sensor_id)
# 'Q' -> unsigned long long (8 bytes, timestamp_ms)
# 'f' -> float (4 bytes, temperature)
# 'f' -> float (4 bytes, pressure)
# 'f' -> float (4 bytes, humidity)
# '32s' -> 32-byte char array (signature)
PACKET_FORMAT = '<hQfff32s'
PACKET_SIZE = struct.calcsize(PACKET_FORMAT) # Debería ser 54 bytes

class SensorTCPHandler(socketserver.BaseRequestHandler):
    """
    El manejador de peticiones para nuestro servidor.
    Se creará una instancia de esta clase por cada conexión entrante.
    """

    def handle(self):
        """
        Este método se ejecuta para cada conexión de un cliente sensor.
        """
        print(f"\n[+] Conexión recibida de {self.client_address[0]}:{self.client_address[1]}")
        
        try:
            # 1. RECIBIR DATOS BINARIOS
            # Leemos exactamente el número de bytes que esperamos para un paquete completo.
            data = self.request.recv(PACKET_SIZE)
            
            # Si no recibimos el tamaño esperado, el paquete es inválido o la conexión se cerró.
            if len(data) < PACKET_SIZE:
                print(f"[!] Paquete incompleto recibido. Se esperaban {PACKET_SIZE} bytes, se recibieron {len(data)}. Descartando.")
                return

            # 2. DESEMPAQUETAR DATOS BINARIOS
            # Usamos struct.unpack para convertir los bytes en tipos de datos de Python.
            unpacked_data = struct.unpack(PACKET_FORMAT, data)
            
            sensor_id = unpacked_data[0]
            timestamp_ms = unpacked_data[1]
            temperature = unpacked_data[2]
            pressure = unpacked_data[3]
            humidity = unpacked_data[4]
            received_signature = unpacked_data[5]

            print(f"[*] Paquete binario desempaquetado para sensor ID: {sensor_id}")

            # 3. VALIDAR LA FIRMA HMAC
            # Para validar, debemos recrear el mensaje original que fue firmado.
            # Este mensaje incluye todos los campos EXCEPTO la propia firma.
            data_to_verify = struct.pack('<hQfff', sensor_id, timestamp_ms, temperature, pressure, humidity)

            # Calculamos la firma HMAC-SHA256 con nuestra clave secreta.
            calculated_signature = hmac.new(HMAC_KEY, data_to_verify, hashlib.sha256).digest()

            # Comparamos las firmas de forma segura para evitar ataques de temporización.
            if not hmac.compare_digest(calculated_signature, received_signature):
                print(f"[!!!] ALERTA DE SEGURIDAD: Firma HMAC inválida para el sensor {sensor_id}. ¡Paquete descartado!")
                return
            
            print(f"[OK] Firma HMAC verificada exitosamente.")

            # 4. TRANSFORMAR A JSON
            # Convertimos el timestamp de Unix (en milisegundos) a formato ISO 8601 en UTC.
            timestamp_dt_utc = datetime.fromtimestamp(timestamp_ms / 1000.0, tz=timezone.utc)
            timestamp_iso = timestamp_dt_utc.isoformat().replace('+00:00', 'Z')

            # Construimos el payload (cuerpo) del JSON para enviar al servidor final.
            json_payload = {
                "sensor_id": sensor_id,
                "timestamp": timestamp_iso,
                "temperature": round(temperature, 2), # Redondeamos para limpieza
                "pressure": round(pressure, 2),
                "humidity": round(humidity, 2)
            }
            
            print(f"[*] Datos transformados a JSON: {json.dumps(json_payload)}")

            # 5. IMPLEMENTAR CLIENTE HTTP PARA REENVIAR
            # Enviamos el payload JSON al servidor final mediante una petición POST.
            try:
                print(f"[*] Reenviando datos al servidor final en {FINAL_SERVER_URL}...")
                response = requests.post(FINAL_SERVER_URL, json=json_payload, timeout=5)
                
                # Verificamos la respuesta del servidor final.
                if 200 <= response.status_code < 300:
                    print(f"[OK] Servidor final respondió con éxito (Código: {response.status_code})")
                else:
                    print(f"[!] Error del servidor final (Código: {response.status_code}): {response.text}")

            except requests.exceptions.RequestException as e:
                # Esto captura errores de red (ej. si el servidor final no está disponible).
                print(f"[!!!] CRÍTICO: No se pudo conectar con el servidor final. Error: {e}")

        except Exception as e:
            print(f"[!] Ocurrió un error inesperado durante el manejo de la conexión: {e}")
        finally:
            print(f"[-] Conexión con {self.client_address[0]}:{self.client_address[1]} cerrada.")


if __name__ == "__main__":
    # Usamos ThreadingTCPServer para que cada cliente sea manejado en su propio hilo.
    # Esto permite que el servidor maneje múltiples sensores concurrentemente.
    with socketserver.ThreadingTCPServer((LISTEN_HOST, LISTEN_PORT), SensorTCPHandler) as server:
        print("==============================================")
        print("     Servidor Intermedio Iniciado")
        print(f"    Escuchando en {LISTEN_HOST}:{LISTEN_PORT}")
        print("==============================================")
        print("Esperando datos binarios de los sensores...")
        
        # Inicia el servidor y lo mantiene corriendo hasta que se detenga manualmente (Ctrl+C).
        server.serve_forever()
      
