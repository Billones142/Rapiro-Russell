# Firmware Rapiro

Sketch de Arduino para la placa de control del robot Rapiro. Debe cargarse en el microcontrolador de la placa Rapiro (compatible con Arduino UNO).

## Requisitos

- [Arduino IDE](https://www.arduino.cc/en/software)
- Cable USB o FTDI para programar la placa Rapiro
- Placa seleccionada: **Arduino UNO**

## Instalación

1. Abre `RAPIRO_ver0_0.ino` en Arduino IDE.
2. Conecta la placa de control Rapiro al PC.
3. Selecciona **Herramientas → Placa → Arduino UNO**.
4. Selecciona el puerto COM correcto.
5. Pulsa **Subir**.

## Conexión con Raspberry Pi

La Raspberry se comunica con la placa Rapiro por UART a **57600 baud**:

| Raspberry Pi | Puerto típico |
|---|---|
| Pi 3/4/5 (UART habilitado) | `/dev/ttyS0` o `/dev/ttyAMA0` |
| Conexión USB-serial | `/dev/ttyUSB0` |

Habilita UART en Raspberry Pi (`raspi-config` → Interface Options → Serial Port).

## Comandos soportados

### Movimientos predefinidos (`#M`)

| Comando | Acción |
|---|---|
| `#M0` | Posición inicial / detener |
| `#M1` | Caminar adelante |
| `#M2` | Caminar atrás |
| `#M3` | Girar derecha |
| `#M4` | Girar izquierda |
| `#M5` | Saludar (mano izq., LED verde) |
| `#M6` | Bajar mano izq. (LED amarillo) |
| `#M7` | Mover ambos brazos (LED azul) |
| `#M8` | Despedirse (LED rojo) |
| `#M9` | Brazo derecho + cintura (LED azul) |

### Pose personalizada (`#P`)

```
#PSxxAyyyTzzz              Servo individual (xx=00-11, ángulo 000-180, tiempo ms)
#PRxxxGyyyBzzzTaaa         LEDs ojos RGB (0-255)
#PS00A090T500#PS01A090T500 Combinar hasta 2 servos + LED
```

### Consultas

| Comando | Respuesta |
|---|---|
| `#C` | Estado del buffer (`#C0` o `#CF`) |
| `#Q` | Tiempo restante del movimiento actual |

## Servomotores (S00-S11)

| ID | Parte |
|---|---|
| S00 | Cabeza (yaw) |
| S01 | Cintura (yaw) |
| S02 | Hombro derecho (roll) |
| S03 | Brazo derecho (pitch) |
| S04 | Mano derecha (grip) |
| S05 | Hombro izquierdo (roll) |
| S06 | Brazo izquierdo (pitch) |
| S07 | Mano izquierda (grip) |
| S08 | Pie derecho (yaw) |
| S09 | Pie derecho (pitch) |
| S10 | Pie izquierdo (yaw) |
| S11 | Pie izquierdo (pitch) |

## LEDs de los ojos

Rapiro usa LEDs RGB con PWM (no NeoPixels direccionables). Se controlan con `#PRxxxGyyyBzzzTaaa`.
