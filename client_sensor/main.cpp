#include <iostream> 
#include <string>    
#include <chrono>    
#include <thread>    
#include <cstdint>   
#include <cstring>   
#include <vector>   
#include <random>    

#include <openssl/hmac.h> 
#include <openssl/sha.h>  
#include <sys/socket.h> // Contiene las funciones principales para la programación de sockets (socket, connect, send, etc.)
#include <netinet/in.h> // Contiene la definición de la estructura sockaddr_in
#include <arpa/inet.h>  // Contiene la función inet_pton para convertir IPs de texto a binario
#include <unistd.h>     // Contiene la función close() para cerrar el socket

#define closesocket close

/**
 * @brief La directiva #pragma pack(push, 1) le indica al compilador que empaquete
 * la estructura con una alineación de 1 byte. Esto elimina cualquier byte de
 * relleno (padding) que el compilador podría agregar para optimizar el acceso a memoria.
 */
#pragma pack(push, 1) //para eliminar padding
struct SensorPacket {
    int16_t sensor_id;            // 2 bytes: Identificador único del sensor
    uint64_t timestamp_ms;        // 8 bytes: Momento de la lectura (Unix Epoch en milisegundos)
    float temperature;            // 4 bytes: Valor de temperatura
    float pressure;               // 4 bytes: Valor de presión
    float humidity;               // 4 bytes: Valor de humedad
    unsigned char signature[32];  // 32 bytes: Firma HMAC-SHA256 para la verificación de datos
};
#pragma pack(pop) // Restaura la configuración de empaquetado original del compilador.

const char* SERVER_IP = "127.0.0.1";                        // La IP del Servidor Intermedio (localhost)
const int SERVER_PORT = 8080;                               // El puerto donde escucha el Servidor Intermedio
const std::string HMAC_KEY = "my-super-secret-key-for-dev"; // La clave secreta compartida para generar la firma
const int16_t SENSOR_ID = 101;                              // El ID de este sensor

/**
 * @brief Calcula la firma HMAC-SHA256 para los campos de datos del paquete.
 * @param packet El paquete con los datos ya llenos (excepto la firma).
 * @param out_signature Un puntero a un buffer de 32 bytes donde se escribirá la firma resultante.
 */

void calculate_hmac(const SensorPacket& packet, unsigned char* out_signature) {
    // --- CÁLCULO DE FIRMA HMAC-SHA256 ---
    // 1. Calculamos el tamaño total de los datos que vamos a firmar.
    // Esto incluye todos los campos del paquete excepto la firma.
    // Usamos sizeof para obtener el tamaño de cada campo.
    // Nota: El tamaño de `packet` es fijo y conocido en tiempo de compilación.
    // Aquí asumimos que la estructura SensorPacket no cambia, por lo que no necesitamos calcular
    // dinámicamente el tamaño de cada campo. Esto es seguro porque hemos definido la estructura con
    // tipos de datos fijos y hemos usado `#pragma pack` para evitar padding.
    size_t data_size = sizeof(packet.sensor_id)
                     + sizeof(packet.timestamp_ms)
                     + sizeof(packet.temperature)
                     + sizeof(packet.pressure)
                     + sizeof(packet.humidity);

    // 2. Creamos un buffer temporal para concatenar todos los campos de datos.
    std::vector<unsigned char> data_buffer(data_size);
    unsigned char* ptr = data_buffer.data(); // Obtenemos un puntero al inicio del buffer.

    // 3. Copiamos los bytes de cada campo, uno tras otro, en el buffer.
    memcpy(ptr, &packet.sensor_id, sizeof(packet.sensor_id));
    ptr += sizeof(packet.sensor_id);
    memcpy(ptr, &packet.timestamp_ms, sizeof(packet.timestamp_ms));
    ptr += sizeof(packet.timestamp_ms);
    memcpy(ptr, &packet.temperature, sizeof(packet.temperature));
    ptr += sizeof(packet.temperature);
    memcpy(ptr, &packet.pressure, sizeof(packet.pressure));
    ptr += sizeof(packet.pressure);
    memcpy(ptr, &packet.humidity, sizeof(packet.humidity));

    // 4. Usamos la función HMAC de OpenSSL para calcular la firma.
    unsigned int signature_len = 32;
    HMAC(
        EVP_sha256(),                   // Algoritmo de hash a usar: SHA256
        HMAC_KEY.c_str(),               // La clave secreta como un string de C
        HMAC_KEY.length(),              // Longitud de la clave
        data_buffer.data(),             // El búfer con los datos concatenados
        data_buffer.size(),             // El tamaño de los datos
        out_signature,                  // Búfer de salida para la firma
        &signature_len                  // Puntero a la longitud de la firma (debe ser 32)
    );
}


// --- FUNCIÓN PRINCIPAL DEL PROGRAMA ---
int main() {
    // --- 1. CONFIGURACIÓN DEL GENERADOR DE DATOS ALEATORIOS ---
    // Usamos el motor de generación Mersenne Twister, que es de alta calidad.
    std::random_device rd;
    std::mt19937 gen(rd());
    // Definimos los rangos para que los datos parezcan realistas.
    std::uniform_real_distribution<> temp_dist(20.0, 30.0);
    std::uniform_real_distribution<> press_dist(1000.0, 1020.0); // en hPa
    std::uniform_real_distribution<> hum_dist(40.0, 60.0);      // en %

    // Mensaje de inicio
    std::cout << "Cliente Sensor C++ iniciado" << std::endl;
    std::cout << "Intentando conectar a " << SERVER_IP << ":" << SERVER_PORT << std::endl;
    std::cout << "Enviando datos cada 5 segundos..." << std::endl;

    // --- 2. BUCLE PRINCIPAL DEL SENSOR ---
    // Este bucle se ejecuta indefinidamente, simulando un sensor que nunca se apaga.
    while (true) {
        SensorPacket packet; // Creamos una instancia del paquete en cada iteración.

        // --- 3. GENERAR DATOS SINTÉTICOS ---
        packet.sensor_id = SENSOR_ID;
        // Obtenemos el tiempo actual del sistema como milisegundos desde el Unix Epoch.
        packet.timestamp_ms = std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::system_clock::now().time_since_epoch()
        ).count();
        // Generamos valores aleatorios para las métricas.
        packet.temperature = static_cast<float>(temp_dist(gen));
        packet.pressure = static_cast<float>(press_dist(gen));
        packet.humidity = static_cast<float>(hum_dist(gen));

        // --- 4. CALCULAR Y ASIGNAR LA FIRMA ---
        calculate_hmac(packet, packet.signature); // Calculamos la firma y la guardamos en `packet.signature`.

        // Imprimimos los datos que se van a enviar para poder monitorear el cliente.
        std::cout << "\n========== Paquete de Sensor ==========" << std::endl;
        std::cout << "Sensor ID    : " << packet.sensor_id << std::endl;
        std::cout << "Timestamp    : " << packet.timestamp_ms << " ms" << std::endl;
        std::cout << "Temperatura  : " << packet.temperature << " °C" << std::endl;
        std::cout << "Presión      : " << packet.pressure << " hPa" << std::endl;
        std::cout << "Humedad      : " << packet.humidity << " %" << std::endl;
        std::cout << "=======================================\n" << std::endl;


        // --- 5. LÓGICA DE RED (CLIENTE TCP) ---
        // Creamos un descriptor de socket. AF_INET para IPv4, SOCK_STREAM para TCP.
        int sock = socket(AF_INET, SOCK_STREAM, 0);
        if (sock == -1) {
            std::cerr << "Error: No se pudo crear el socket." << std::endl;
            std::this_thread::sleep_for(std::chrono::seconds(5)); // Esperar antes de reintentar
            continue; // Saltar al siguiente ciclo del bucle
        }

        // Configuramos la estructura con la dirección del servidor.
        sockaddr_in server_addr;
        server_addr.sin_family = AF_INET; // Familia de direcciones IPv4
        // Convertimos el puerto a "Network Byte Order" (Big Endian).
        server_addr.sin_port = htons(SERVER_PORT);
        // Convertimos la IP de texto a formato binario de red.
        inet_pton(AF_INET, SERVER_IP, &server_addr.sin_addr);

        // Intentamos establecer la conexión con el servidor.
        if (connect(sock, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
            std::cerr << "Error: Fallo en la conexión al servidor." << std::endl;
            closesocket(sock); // Cerramos el socket si la conexión falla.
            std::this_thread::sleep_for(std::chrono::seconds(5)); // Esperamos antes de reintentar.
            continue;
        }
        
        std::cout << "Conectado al servidor. Enviando paquete de " << sizeof(packet) << " bytes." << std::endl;

        // Enviamos la estructura completa como un flujo de bytes.
        // Se envía la dirección de memoria de `packet` y su tamaño total.
        if (send(sock, (const char*)&packet, sizeof(packet), 0) < 0) {
            std::cerr << "Error: Fallo al enviar los datos." << std::endl;
        } else {
            std::cout << "Paquete enviado exitosamente." << std::endl;
        }

        // Cerramos la conexión después de enviar los datos.
        closesocket(sock);

        // --- 6. ESPERAR ANTES DE LA PRÓXIMA LECTURA ---
        std::this_thread::sleep_for(std::chrono::seconds(5));
    }
}