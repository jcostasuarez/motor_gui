import spidev

class SPIHandler:
    def __init__(self, device, speed):
        self.device = device
        self.speed = speed
        self.spi = spidev.SpiDev()
        self.connected = False
        self.connect()

    def connect(self):
        try:
            bus, device = map(int, self.device.split('.')[-2:])
            self.spi.open(bus, device)
            self.spi.max_speed_hz = self.speed
            self.connected = True
            print("SPI conectado correctamente.")
        except Exception as e:
            self.connected = False
            print(f"Error al conectar SPI: {e}")

    def send_command(self, command):
        if not self.connected:
            print("SPI no está conectado. No se puede enviar el comando.")
            return None
        try:
            data = [ord(c) for c in command]
            response = self.spi.xfer2(data)
            print(f"Comando enviado: {command}, Respuesta: {response}")
            return response
        except Exception as e:
            print(f"Error enviando comando SPI: {e}")
            self.connected = False  # Marcar como desconectado si ocurre un error
            return None

    def close(self):
        if self.connected:
            self.spi.close()
            self.connected = False
            print("SPI desconectado.")


