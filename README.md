===================================================================
                INSTRUCCIONES DE EJECUCIÓN DEL PROYECTO
===================================================================
Paso 0: Requisitos Previos
-------------------------------------------------------------------

1. Instalar Git
2. Instalar Python 3.8 o superior
3. Instalar un compilador de C++ (g++ es estándar en Linux).
4. Instalar las librerías de desarrollo de OpenSSL.
   - En Debian/Ubuntu: sudo apt-get install libssl-dev

   *Librerías necesarias para Cliente Sensor.
-------------------------------------------------------------------
Paso 1: Clonar el Repositorio
-------------------------------------------------------------------

Abrir una terminal y ejecuta los siguientes comandos:

git clone https://github.com/JavierKDGN/ProyectoRedes.git

-------------------------------------------------------------------
Paso 2: Ejecutar Módulo 3 (Servidor Final - FastAPI)
-------------------------------------------------------------------

En una Terminal:

1. Navegar a la carpeta del servidor final:
   cd ~/ProyectoRedes/final_server/

2. Crear entorno virtual:
   python -m venv venv

3. Activar entorno virtual:
   source venv/bin/activate

4. Instalar dependencias:

	pip install "fastapi[all]"

	pip install sqlalchemy

	pip install pandas

5. Ejecutar el servidor FastAPI:
   uvicorn app.final_server:app --reload

   *Mostrará que está corriendo en http://127.0.0.1:8000.
   *Dejar terminal abierta.

-------------------------------------------------------------------
Paso 3: Ejecutar Módulo 2 (Servidor Intermedio)
-------------------------------------------------------------------

En una segunda Terminal:

1. Navegar a la carpeta del servidor intermedio:
   cd ~/ProyectoRedes/intermediate_server/

2. Crear entorno virtual:
   python3 -m venv venv

3. Activar entorno virtual:
   source venv/bin/activate

4. Instalar dependencias:

   	pip install requests

	pip install pymodbus

5. Ejecutar el servidor:
   python3 intermediate_server.py

   *Mostrará que está escuchando en el puerto 8080 y 502.
   *Dejar terminal abierta.

-------------------------------------------------------------------
Paso 4: Ejecutar Módulo 1 (Cliente Sensor - C++)
-------------------------------------------------------------------

En una tercera Terminal:

1. Navegar a la carpeta del cliente:
   cd ~/ProyectoRedes/client_sensor/

2. Compilar el código para crear el programa:
   g++ main.cpp -o sensor_client -lssl -lcrypto

3. Ejecutar el cliente:
   ./sensor_client

   *Mostrará cómo se envían paquetes de datos cada 5 segundos.
   *Dejar terminal abierta.

-------------------------------------------------------------------
Paso 5: Ver Resultados
-------------------------------------------------------------------

Página Web:

1. Abrir navegador e ingresar a: http://127.0.0.1:8000

2. En el campo "ID Sensor", escribir '101' y presionar "Aplicar Filtros".
   
   *Se mostrarán las gráficas, estadísticas y lecturas recientes en tiempo real.

-------------------------------------------------------------------
Paso 6: Ejecutar Módulo 4 (Cliente de Consulta de Alertas)
-------------------------------------------------------------------

En una cuarta Terminal:

1. Navegar a la carpeta del cliente de consulta:
   cd ~/ProyectoRedes/query_client/

2. Crear entorno virtual:
   python3 -m venv venv

3. Activar entorno virtual:
   source venv/bin/activate

4. Instalar dependencias:
   	
	pip install aiohttp
   	
	pip install pydantic

5. Ejecutar el cliente de consulta:
   python query_client.py

   *Se mostrarán las últimas lecturas y saltarán alertas si los valores
    se salen de los rangos definidos.
   *Dejar terminal abierta.

-------------------------------------------------------------------
Paso Final: Cómo Detener Todo el Sistema
-------------------------------------------------------------------

Ir a cada una de las cuatro terminales abiertas y presionar Ctrl + C

*Esto cerrará cada módulo de forma segura.
