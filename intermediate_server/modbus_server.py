import threading
from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext

#Direccion y puerto donde el servidor Modbus escuchará
MODBUS_HOST = "0.0.0.0"
MODBUS_PORT = 502           #Puerto estándar para Modbus TCP

#Contexto de Modbus que contiene los registros
MODBUS_CONTEXT = None
#Lock para garantizar acceso seguro entre hilos
MODBUS_LOCK = threading.Lock()

#Se crea el almacén de datos para Modbus.
def initialize_datastore():
    #Inicializa y devuelve el contexto del servidor Modbus.
    global MODBUS_CONTEXT
    
    #Se usan "Input Registers". Tamaño: 10 registros.
    #Se inicializan los registros a 0.
    data_block = ModbusSequentialDataBlock(0, [0] * 10)
    #Se crea un contexto esclavo.
    slave_context = ModbusSlaveContext(ir=data_block)
    #Se define el contexto global del servidor.
    MODBUS_CONTEXT = ModbusServerContext(slaves=slave_context, single=True)
    print("[MODBUS] Almacén de datos (datastore) inicializado.")

#Función para actualizar de forma segura los registros del servidor Modbus.
def update_modbus_registers(sensor_id: int, temperature: float, pressure: float, humidity: float):
    with MODBUS_LOCK:
        #Se los convierten los floats multiplicando, porque los registros Modbus son enteros. 
        temp_scaled = int(temperature * 100)
        press_scaled = int(pressure * 10)
        hum_scaled = int(humidity * 100)

        #Se crea una lista de valores a escribir
        values = [sensor_id, temp_scaled, press_scaled, hum_scaled]
        
        # El primer argumento 3 se refiere a Holding Registers.
        # El segundo argumento es la dirección de inicio.
        MODBUS_CONTEXT[0].setValues(3, 0, values) # 3 = Holding, 4 = Input
        
        print(f"[MODBUS] Registros actualizados: ID={values[0]}, Temp={values[1]}, Press={values[2]}, Hum={values[3]}")

#Función que se ejecuta en un hilo para iniciar el servidor
def run_modbus_server_thread():
    print(f"[MODBUS] Iniciando servidor Modbus en {MODBUS_HOST}:{MODBUS_PORT}")
    StartTcpServer(context=MODBUS_CONTEXT, address=(MODBUS_HOST, MODBUS_PORT))
