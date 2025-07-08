README hecho por nosotros, IA fue usada para estilizar el markdown (Gemini 2.5 Pro) 



# INSTRUCCIONES DE EJECUCIÓN DEL PROYECTO

-------------------------------------------------------------------
Paso 0: Requisitos Previos
-------------------------------------------------------------------


* **Git**
* **Python 3.8+**
* **Compilador de C++ (g++ es estándar en Linux)**.
* **Librerías de desarrollo de OpenSSL**.
   - En Debian/Ubuntu: `sudo apt-get install libssl-dev`

-------------------------------------------------------------------
Paso 1: Clonar el Repositorio
-------------------------------------------------------------------

Se abre una terminal y se ejecutan los siguientes comandos:

```bash
git clone https://github.com/JavierKDGN/ProyectoRedes.git
cd ProyectoRedes
```

-------------------------------------------------------------------
Paso 2: Preparacion de entorno
-------------------------------------------------------------------
En la terminal creamos y activamos un entorno virtual para los componentes con Python:
```bash
    python -m venv .venv
    # En Linux
    source .venv/bin/activate
```

Luego se instalan todas las dependencias de Python
* Usando el archivo `requirements.txt` que agrupa lo necesario
```bash
pip install -r requirements.txt
```

Por ultimo se compila el cliente sensor de C++:
```bash
cd client_sensor/
g++ main.cpp -o sensor_client -lssl -lcrypto
``` 

-------------------------------------------------------------------
Paso 3: Ejecucion del sistema
-------------------------------------------------------------------

Para que todo funcione, se deben ejecutar todos los componentes en el orden correcto. **Se necesitaran 4 terminales separadas**, y tener activado el entorno virtual del paso 2 (`source .venv/bin/activate`).

#### **Terminal 1: Iniciar la API (Python/FastAPI)**
*Debe ejecutarse primero, porque es el destino final de los datos.*

```bash
cd final_server/
# uvicorn viene con FastAPI y ayuda a correr la documentacion
uvicorn app.final_server:app --reload
```
> Indicara que el servidor esta corriendo en `http://127.0.0.1:8000`.

---

#### **Terminal 2: Servidor intermedio (Python)**
*Escucha al sensor y reenvia los datos a la API*

```bash
cd intermediate_server/
python intermediate_server.py
```
> Indicara que el servidor está escuchando en el puerto `8080`.

---

#### **Terminal 3: Iniciar el Cliente Sensor (C++)**
*Este componente simula el sensor y comenzará a enviar datos.*

```bash
cd client_sensor/
./sensor_client
```
> 🖥️ Verás mensajes de "Paquete enviado exitosamente" cada 5 segundos.

---

#### **Terminal 4 (Opcional): Cliente de Consulta**
*Este cliente monitorea los datos y muestra alertas.*

```bash
cd query_client/
python query_client.py
```
> Recibira lecturas de datos y alertara si algún valor excede los límites predefinidos.

## Verificación y Resultados

1.  **Dashboard Web**: Abre el navegador y ve a **[http://127.0.0.1:8000](http://127.0.0.1:8000)**.
2.  **Filtrar Datos**: Haz clic en "Aplicar Filtros", mostrara los datos de todos los sensores.

3. **Mostrara en tiempo real**:
    *   Un gráfico con la humedad.
    *   Estadísticas de los datos recibidos.
    *   Una tabla con las últimas lecturas.


-------------------------------------------------------------------
Paso Final: Cómo Detener Todo el Sistema
-------------------------------------------------------------------

Ir a cada una de las cuatro terminales abiertas y presionar Ctrl + C

*Esto cerrará cada módulo de forma segura.*


## Estructura del Proyecto
```
proyecto_final/
├── .venv/                  # Entorno virtual de Python
├── client_sensor/          # Módulo 1: Cliente C++ que simula el sensor
├── final_server/           # Módulo 3: Servidor FastAPI, base de datos y dashboard
├── intermediate_server/    # Módulo 2: Servidor Python que actúa como gateway
├── query_client/           # Módulo 4: Cliente Python para monitoreo y alertas
└── requirements.txt        # Archivo con todas las dependencias de Python
```

---
### Autores
*   Javier Cadagan
*   Mariel Muñoz
*   Jhostian San Martin

