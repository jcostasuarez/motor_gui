from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from spi.spi_handler import SPIHandler

Builder.load_file('gui/layout.kv')

class MotorControlLayout(BoxLayout):
    def __init__(self, spi_handler, **kwargs):
        super().__init__(**kwargs)
        self.spi_handler = spi_handler
        if not self.spi_handler.connected:
            self.ids.status_label.text = "Error: No hay conexión SPI"

    def set_speed(self, speed):
        response = self.spi_handler.send_command(f"SET_SPEED:{speed}")
        if response is None:
            self.ids.status_label.text = "Error: Fallo en la comunicación SPI"
        else:
            self.ids.status_label.text = f"Velocidad ajustada a {speed}"
            self.update_tachometer(speed)

    def toggle_motor(self):
        if self.spi_handler.connected:
            if self.ids.toggle_button.text == "Encender":
                self.spi_handler.send_command("MOTOR:ON")
                self.ids.toggle_button.text = "Apagar"
            else:
                self.spi_handler.send_command("MOTOR:OFF")
                self.ids.toggle_button.text = "Encender"
        else:
            self.ids.status_label.text = "Error: No hay conexión SPI"

    def reconnect_spi(self):
        self.spi_handler.connect()
        if self.spi_handler.connected:
            self.ids.status_label.text = "Reconexión SPI exitosa"
        else:
            self.ids.status_label.text = "Error: No se pudo reconectar SPI"

    def update_tachometer(self, rpm):
        self.ids.tachometer_label.text = f'RPM: {rpm}'

class MotorControlApp(App):
    def build(self):
        spi_handler = SPIHandler('/dev/spidev0.0', 500000)
        return MotorControlLayout(spi_handler)

if __name__ == '__main__':
    MotorControlApp().run()
