import serial
import time


class Rapiro:
    def __init__(self, port="/dev/ttyAMA0", baudrate=57600):
        self.port = port
        self.baudrate = baudrate

    def send(self, command, wait=1.8):
        print(f"Enviando: {command}")
        with serial.Serial(self.port, self.baudrate, timeout=1) as com:
            time.sleep(0.5)
            com.write((command + "\r").encode("ascii"))
            com.flush()
            time.sleep(wait)

    def reset(self):
        self.send("#M0", wait=2.0)

    def caminar_adelante(self):
        self.send("#M1", wait=1.8)

    def caminar_atras(self):
        self.send("#M2", wait=1.8)

    def brazo_derecho(self):
        self.send("#M6", wait=1.2)

    def brazo_izquierdo(self):
        self.send("#M8", wait=1.2)

    def brazos_ambos(self):
        self.send("#M5", wait=1.5)

    def ojos(self, r, g, b, t=10):
        cmd = f"#PR{r:03d}G{g:03d}B{b:03d}T{t:03d}"
        self.send(cmd, wait=0.2)


if __name__ == "__main__":
    rapiro = Rapiro()

    try:
        # Estado inicial
        rapiro.reset()
        rapiro.ojos(0, 0, 255)   # azul

        # 4 ciclos adelante con brazos alternados
        for i in range(4):
            print(f"Adelante {i+1}/4")
            rapiro.caminar_adelante()

            if i % 2 == 0:
                rapiro.brazo_derecho()
            else:
                rapiro.brazo_izquierdo()

        # pausa breve
        rapiro.reset()
        time.sleep(1)

        # 4 ciclos atrás con brazos alternados
        for i in range(4):
            print(f"Atrás {i+1}/4")
            rapiro.caminar_atras()

            if i % 2 == 0:
                rapiro.brazo_izquierdo()
            else:
                rapiro.brazo_derecho()

        # saludo final
        rapiro.ojos(0, 255, 0)   # verde
        rapiro.brazos_ambos()
        rapiro.reset()

    except Exception as e:
        print("Error:", e)