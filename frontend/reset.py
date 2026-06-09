import sys
import time
from gpiozero import DigitalOutputDevice

# Pin GPIO por defecto para el RESET (por ejemplo, GPIO 18)
DEFAULT_RESET_PIN = 18

def reset_microcontroller(pin_number):
    print(f"Reiniciando el microcontrolador a través del pin GPIO {pin_number} con gpiozero...")
    try:
        # El pin de RESET de Arduino es activo en BAJO (active-low).
        # Debe estar en HIGH (3.3V) y bajar a LOW (0V) para resetear el chip.
        reset_pin = DigitalOutputDevice(pin_number, active_high=True, initial_value=True)
        
        # Generar pulso de reset
        reset_pin.off()  # Pone el pin en LOW (0V)
        time.sleep(0.15) # Espera 150 ms
        reset_pin.on()   # Pone el pin en HIGH (3.3V)
        
        print("¡Reinicio del microcontrolador completado! El bootloader está listo para recibir el firmware.")
    except Exception as e:
        print(f"Error al controlar el pin GPIO {pin_number} con gpiozero: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    gpio_pin = DEFAULT_RESET_PIN
    if len(sys.argv) > 1:
        try:
            gpio_pin = int(sys.argv[1])
        except ValueError:
            print(f"Uso: python3 reset.py [numero_pin_gpio]")
            print(f"Usando pin por defecto: GPIO {DEFAULT_RESET_PIN}")
            
    reset_microcontroller(gpio_pin)
