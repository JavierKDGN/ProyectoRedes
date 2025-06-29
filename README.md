# Proyecto: Plataforma IoT Distribuida y Segura
(Readme generado por Gemini 2.5 Pro)

Este repositorio contiene el código fuente para el proyecto semestral de Redes de Computadores. El objetivo es diseñar e implementar un sistema distribuido que simula un entorno de monitoreo industrial, manejando la transmisión, almacenamiento y análisis de datos de sensores.

## Arquitectura del Sistema

El sistema se compone de cuatro módulos que se comunican en una cadena de procesamiento:

`[1. Cliente Sensor (C++)]`

`[2. Servidor Intermedio (Python)]`

`[3. Servidor Final (FastAPI Python)]`

`[4. Cliente de Consulta (Python)]`

**Flujo de Datos:**

1.  El **Cliente Sensor** genera datos y los envía en formato binario a través de un socket TCP.
2.  El **Servidor Intermedio** recibe los datos binarios, los valida, los transforma a formato JSON y los reenvía mediante una petición HTTP POST.
3.  El **Servidor Final** recibe el JSON, lo valida y lo almacena en una base de datos SQLite. Expone los datos a través de una API REST.
4.  El **Cliente de Consulta** consume la API REST periódicamente para monitorear los datos y generar alertas si los valores están fuera de los rangos permitidos.

---

## Contratos de Datos (Data Contracts)

Para que el sistema funcione, todos los componentes deben adherirse estrictamente a los siguientes formatos.

### 1. Paquete Binario (Sensor -> Servidor Intermedio)

La comunicación se realiza mediante una `struct` de C++ con empaquetado de 1 byte para evitar relleno.

*   **Endianness:** Little Endian (estándar en x86/x64).
*   **Firma:** HMAC-SHA256. La clave secreta compartida para desarrollo es: `my-super-secret-key-for-dev`.
*   **Definición de la `struct` en C++:**

```cpp
#pragma pack(push, 1)
struct SensorPacket {
    int16_t sensor_id;          // 2 bytes
    uint64_t timestamp_ms;      // 8 bytes (Unix Epoch en milisegundos)
    float temperature;          // 4 bytes
    float pressure;             // 4 bytes
    float humidity;             // 4 bytes
    unsigned char signature[32];  // 32 bytes (HMAC-SHA256)
};
#pragma pack(pop)
```

*   **Tamaño Total del Paquete:** 54 bytes.

### 2. Payload JSON (Servidor Intermedio -> Servidor Final)

El Servidor Intermedio enviará una petición `HTTP POST` a la ruta `/readings/` del Servidor Final con el siguiente cuerpo en formato JSON.

*   **`Content-Type` Header:** `application/json`
*   **Formato del Timestamp:** ISO 8601 en UTC (ej: `"2023-10-27T21:45:15.123Z"`).
*   **Estructura del JSON:**

```json
{
  "sensor_id": 101,
  "timestamp": "2023-10-27T21:45:15.123Z",
  "temperature": 45.5,
  "pressure": 101.3,
  "humidity": 35.2
}
```

---

## Componentes y Tareas Pendientes

### 1. Cliente Sensor (`client-sensor-cpp/`)

Simula un sensor que genera y envía datos.

*   **Tecnología:** C++
*   **Responsable:** [Nombre del Alumno]
*   **Tareas (To-Do List):**
    *   [ ] **1. Implementar la `struct SensorPacket`:** Definir la estructura de datos exactamente como se especifica en el contrato.
    *   [ ] **2. Generar Datos Sintéticos:** Crear una función que genere valores aleatorios pero realistas para temperatura, presión y humedad.
    *   [ ] **3. Calcular Firma HMAC:** Implementar la lógica para calcular el HMAC-SHA256 de los campos de datos usando una librería criptográfica (ej. OpenSSL).
    *   [ ] **4. Lógica de Cliente TCP:** Crear un cliente de socket TCP que se conecte a la IP y puerto del Servidor Intermedio.
    *   [ ] **5. Bucle Principal:** Crear un bucle que periódicamente (ej. `sleep(5)`):
        *   Genere nuevos datos.
        *   Calcule la firma.
        *   Ensamble la `struct SensorPacket`.
        *   Envíe la estructura serializada por el socket.

### 2. Servidor Intermedio (`intermediate-server-python/`)

Recibe datos binarios, los valida, transforma y reenvía.

*   **Tecnología:** Python
*   **Responsable:** [Nombre del Alumno]
*   **Tareas (To-Do List):**
    *   [ ] **1. Implementar Servidor TCP:** Usar `socketserver` o `asyncio` para crear un servidor TCP que escuche conexiones entrantes. Debe ser capaz de manejar múltiples clientes.
    *   [ ] **2. Desempaquetar Datos Binarios:** Al recibir datos, leer exactamente 54 bytes y usar `struct.unpack()` con la cadena de formato correcta (`'<hQfff32s'`) para extraer los valores.
    *   [ ] **3. Validar Firma HMAC:** Recalcular el HMAC-SHA256 de los datos recibidos y compararlo con la firma del paquete. Descartar paquetes inválidos.
    *   [ ] **4. Transformar a JSON:** Construir un diccionario de Python con los datos y convertir el timestamp a formato ISO 8601.
    *   [ ] **5. Implementar Cliente HTTP:** Usar la librería `requests` para enviar el diccionario como JSON (`json=payload`) al endpoint `/readings/` del Servidor Final.
    *   [ ] **6. Manejo de Errores:** Implementar bloques `try...except` para manejar fallos de red (si el Servidor Final no responde).

### 3. Servidor Final y API (`final-server-fastapi/`)

Almacena y expone los datos a través de una API REST.

*   **Tecnología:** Python, FastAPI, SQLModel
*   **Responsable:** [Tu Nombre]
*   **Tareas (To-Do List):**
    *   [ ] **1. Configurar Proyecto FastAPI:** Estructurar el proyecto en módulos (`main.py`, `models.py`, `crud.py`, `database.py`).
    *   [ ] **2. Definir Modelos (SQLModel):** En `models.py`, crear el modelo `SensorReading` que sirva tanto para la tabla de la base de datos (SQLite) como para la validación de la API.
    *   [ ] **3. Crear Lógica de Base de Datos (CRUD):** En `crud.py`, implementar las funciones para crear (`create_sensor_reading`) y leer (`get_sensor_readings`) registros.
    *   [ ] **4. Implementar Endpoints de la API:** En `main.py`:
        *   Crear el endpoint `POST /readings/` que recibe datos del Servidor Intermedio y los guarda en la BD.
        *   Crear el endpoint `GET /readings/` que devuelve los datos almacenados. Permitir parámetros de consulta como `limit`.
    *   [ ] **(Stretch Goal) 5. Visualización Web:** Servir un archivo HTML/JS simple que consulte el endpoint GET y muestre los datos en una tabla o gráfica.

### 4. Cliente de Consulta (`query-client-python/`)

Monitorea los datos de la API y genera alertas.

*   **Tecnología:** Python, `httpx`, `asyncio`
*   **Responsable:** [Nombre del Alumno]
*   **Tareas (To-Do List):**
    *   [ ] **1. Configurar el Cliente Asíncrono:** Usar `httpx.AsyncClient` para las peticiones HTTP.
    *   [ ] **2. Implementar Bucle de Monitoreo:** Crear una función `async` que se ejecute en un bucle infinito (`while True`).
    *   [ ] **3. Consultar la API:** Dentro del bucle, hacer una petición `GET` al endpoint `/readings/` del Servidor Final y esperar (`await`) la respuesta.
    *   [ ] **4. Analizar Datos:** Recorrer los datos recibidos y compararlos con umbrales predefinidos (ej. `if temperature > 90.0`).
    *   [ ] **5. Generar Alertas:** Si una condición se cumple, imprimir un mensaje de alerta claro en la consola.
    *   [ ] **6. Espera Asíncrona:** Usar `await asyncio.sleep()` para pausar entre cada ciclo de consulta.

---
Este README.md proporciona una guía clara y centralizada. Asegúrate de que todos los miembros del equipo lo lean y estén de acuerdo antes de comenzar a codificar.