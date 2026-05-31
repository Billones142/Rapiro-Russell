import serial
import time

# Configuración del puerto serie
# Nota: En Raspberry Pi, el puerto suele ser '/dev/ttyS0' o '/dev/ttyAMA0'
# Si estás conectado por cable USB directamente a la placa, podría ser '/dev/ttyUSB0'
PUERTO_SERIE = '/dev/ttyS0' 
BAUDIOS = 57600

def enviar_comando(ser, comando):
    """Envía un comando serial al Rapiro asegurando el salto de línea."""
    print(f"Enviando: {comando}")
    ser.write(f"{comando}\r".encode('utf-8')) # Rapiro espera un retorno de carro (\r)
    time.sleep(1) # Pausa para dar tiempo a procesar la acción

try:
    # Inicializar la conexión serie
    with serial.Serial(PUERTO_SERIE, BAUDIOS, timeout=1) as rapiro:
        print("Conexión establecida con Rapiro.")
        time.sleep(2)  # Espera para que la placa se estabilice tras abrir el puerto

        # 1. Volver a la posición inicial (Detenerse)
        enviar_comando(rapiro, "#M0")
        time.sleep(2)

        # 2. Caminar hacia adelante
        enviar_comando(rapiro, "#M1")
        time.sleep(4)  # Camina durante 4 segundos

        # 3. Detenerse y ponerse en alerta
        enviar_comando(rapiro, "#M0")
        
        # 4. Cambiar el color de los ojos usando comandos de LED directos
        # Formato: #P[Rojo][Verde][Azul] con valores de 000 a 255
        print("Cambiando ojos a color verde...")
        enviar_comando(rapiro, "#P000255000")
        time.sleep(2)

        print("Cambiando ojos a color rojo...")
        enviar_comando(rapiro, "#P255000000")
        time.sleep(2)

        # 5. Saludar (Comando de movimiento predefinido #M5)
        enviar_comando(rapiro, "#M5")
        time.sleep(3)

        # Volver a posición neutra final
        enviar_comando(rapiro, "#M0")
        print("Rutina finalizada.")

except serial.SerialException:
    print(f"Error: No se pudo abrir el puerto {PUERTO_SERIE}. Verifica los permisos o el nombre del puerto.")
except KeyboardInterrupt:
    print("\nPrograma interrumpido por el usuario.")