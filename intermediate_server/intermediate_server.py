import socketserver
import struct
import hmac
import hashlib
import json
import requests
import threading
import time
from datetime import datetime, timezone

import modbus_server

#Direccion y puerto donde el servidor intermedio escuchará las conexiones TCP del sensor C++
LISTEN_HOST = "0.0.0.0"  # Escuchar en todas las interfaces de red disponibles
LISTEN_PORT = 8080

#URL del Servidor Final (FastAPI) al que se reenviarán los datos
FINAL_SERVER_URL = "http://localhost:8000/readings/"

#Clave secreta compartida para la verificación HMAC. Misma que en el cliente C++.
HMAC_KEY = b"clave_secreta_1111"

#Definición del formato del paquete binario y su tamaño.
PACKET_FORMAT = '<hQfff32s'
#Corresponde a la struct SensorPacket de C++: <h Q f f f 32s>
# '<' -> Little-endian
# 'h' -> short (2 bytes, sensor_id)
# 'Q' -> unsigned long long (8 bytes, timestamp_ms)
# 'f' -> float (4 bytes, temperature)
# 'f' -> float (4 bytes, pressure)
# 'f' -> float (4 bytes, humidity)
# '32s' -> 32-byte char array (signature)

#Definición del tamaño del paquete binario .
PACKET_SIZE = struct.calcsize(PACKET_FORMAT) # Debería ser 54 bytes

#Manejador de peticiones para nuestro servidor.
#Se creará una instancia de esta clase por cada conexión entrante.
class SensorTCPHandler(socketserver.BaseRequestHandler):

    #Este método se ejecuta para cada conexión de un cliente sensor.
    def handle(self):
        print(f"\n[+] Conexión recibida de {self.client_address[0]}:{self.client_address[1]}")
        
        try:
            #RECIBIR DATOS BINARIOS: Leemos el número de bytes esperado para un paquete completo.
            data = self.request.recv(PACKET_SIZE)
            
            #Si no se recibe el tamaño esperado, el paquete es inválido o la conexión se cerró.
            if len(data) < PACKET_SIZE:
                print(f"[!] Paquete incompleto, se esperaban {PACKET_SIZE} bytes, se recibieron {len(data)}. (Descartando...)")
                return

            #DESEMPAQUETAR DATOS BINARIOS: Usamos struct.unpack para convertir los bytes en tipos de datos de Python.
            datos_desempaquetados = struct.unpack(PACKET_FORMAT, data)
            
            sensor_id = datos_desempaquetados[0]             # 'h'
            timestamp_ms = datos_desempaquetados[1]          # 'Q'
            temperature = datos_desempaquetados[2]           # 'f'
            pressure = datos_desempaquetados[3]              # 'f'
            humidity = datos_desempaquetados[4]              # 'f'
            received_signature = datos_desempaquetados[5]    # '32s'

            print(f"[*] Paquete binario desempaquetado para sensor ID: {sensor_id}")

            #VALIDAR LA FIRMA HMAC:
            #Para validar, debemos recrear el mensaje original que fue firmado.
            #El mensaje incluye todos los campos menos la firma.
            data_to_verify = struct.pack('<hQfff', sensor_id, timestamp_ms, temperature, pressure, humidity)

            #Calculamos la firma HMAC-SHA256 con la clave secreta compartida.
            calculated_signature = hmac.new(HMAC_KEY, data_to_verify, hashlib.sha256).digest()

            #Comparamos las firmas de forma segura, para evitar ataques de temporización.
            if not hmac.compare_digest(calculated_signature, received_signature):
                print(f"[!!] ALERTA DE SEGURIDAD: Firma HMAC inválida para el sensor {sensor_id}. Paquete descartado.")
                return
            
            print(f"[OK] Firma HMAC verificada exitosamente.")
            
            #Se llama a la función del archivo modbus_server
            print("[*] Actualizando registros Modbus...")
            modbus_server.update_modbus_registers(sensor_id, temperature, pressure, humidity)

            #TRANSFORMAR A JSON:
            #Primero, convertimos el timestamp de Unix (en milisegundos) a formato ISO 8601 en UTC.
            timestamp_dt_utc = datetime.fromtimestamp(timestamp_ms / 1000.0, tz=timezone.utc)
            timestamp_iso = timestamp_dt_utc.isoformat().replace('+00:00', 'Z')

            #Construimos el payload (cuerpo) del archivo JSON para enviar al servidor final.
            json_payload = {
                "sensor_id": sensor_id,
                "timestamp": timestamp_iso,
                "temperature": round(temperature, 2),
                "pressure": round(pressure, 2),
                "humidity": round(humidity, 2)
            }
            
            print(f"[*] Datos transformados a JSON: {json.dumps(json_payload)}")

            #IMPLEMENTAR CLIENTE HTTP PARA REENVIAR: Enviamos el payload JSON al servidor final mediante una petición POST.
            try:
                print(f"[*] Reenviando datos al servidor final en {FINAL_SERVER_URL}...")
                respuesta = requests.post(FINAL_SERVER_URL, json=json_payload, timeout=5)
                
                #Se verifica la respuesta del servidor final.
                if 200 <= respuesta.status_code < 300: #Códigos de exito en HTTP (200-299)
                    print(f"[OK] Servidor final respondió con éxito (Código: {respuesta.status_code})")
                else:
                    print(f"[!] Error del servidor final (Código: {respuesta.status_code}): {respuesta.text}")

            except requests.exceptions.RequestException as e:
                #Esta excepción capturará errores de red, por ejemplo, si el servidor final no está disponible.
                print(f"[!!] ERROR: No se pudo conectar con el servidor final. (Error: {e})")

        except Exception as e:
            print(f"[!] Ocurrió un error inesperado durante la conexión: {e}")
        finally:
            print(f"[-] Conexión con {self.client_address[0]}:{self.client_address[1]} cerrada.")


if __name__ == "__main__":
    #Se inicializa el datastore del servidor Modbus.
    modbus_server.initialize_datastore()
    
    #Se crea y se inicia el hilo del servidor Modbus.
    modbus_thread = threading.Thread(target=modbus_server.run_modbus_server_thread)
    modbus_thread.daemon = True
    modbus_thread.start()
    time.sleep(1)

    
    #Se inicia el servidor TCP usando ThreadingTCPServer, para que cada cliente sea manejado en su propio hilo.
    #Esto permite al servidor manejar múltiples sensores concurrentemente.
    with socketserver.ThreadingTCPServer((LISTEN_HOST, LISTEN_PORT), SensorTCPHandler) as server:
        print("===================================================")
        print("     Servidor Intermedio Iniciado")
        print(f"    Escuchando conexiones en {LISTEN_HOST}:{LISTEN_PORT}")
        print(f"    Escuchando Modbus TCP en el puerto {modbus_server.MODBUS_PORT}")
        print("===================================================")
        print("Esperando datos binarios de los sensores...")
        
        #Inicia el servidor y lo mantiene corriendo hasta que se detenga manualmente (con Ctrl+C).
        server.serve_forever()
      
