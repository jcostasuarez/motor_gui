# Archivo: spi_tab.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
import spidev

# Paleta de colores basada en motor_control_ui.py
PRIMARY_COLOR = (0.0, 0.32, 0.63, 1)  # Azul UTN
SECONDARY_COLOR = (0.8, 0.8, 0.8, 1)  # Gris claro
TEXT_COLOR = (1, 1, 1, 1)             # Blanco

class SPITab(BoxLayout):
    def __init__(self, terminal_callback, **kwargs):
        super().__init__(orientation='vertical', spacing=10, padding=10, **kwargs)

        self.terminal_callback = terminal_callback
        self.spi_connected = False
        self.spi = spidev.SpiDev()

        # Indicador de estado
        self.connection_status = Label(
            text="Estado: Desconectado",
            size_hint=(1, 0.1),
            color=(1, 0, 0, 1)  # Rojo para desconectado
        )
        self.add_widget(self.connection_status)

        # Configuración SPI
        config_layout = BoxLayout(size_hint=(1, 0.1), spacing=10)
        config_label = Label(text="Puerto SPI:", size_hint=(0.3, 1), color=PRIMARY_COLOR)
        self.spi_port_selector = Spinner(
            text="SPI0",
            values=("SPI0", "SPI1"),
            size_hint=(0.7, 1),
            background_color=PRIMARY_COLOR,
            color=TEXT_COLOR
        )
        config_layout.add_widget(config_label)
        config_layout.add_widget(self.spi_port_selector)
        self.add_widget(config_layout)

        # Velocidad de transmisión
        speed_layout = BoxLayout(size_hint=(1, 0.1), spacing=10)
        speed_label = Label(text="Velocidad (Hz):", size_hint=(0.3, 1), color=PRIMARY_COLOR)
        self.speed_input = TextInput(text="500000", multiline=False, size_hint=(0.7, 1))
        speed_layout.add_widget(speed_label)
        speed_layout.add_widget(self.speed_input)
        self.add_widget(speed_layout)

        # Botón Intentar conexión
        connect_button = Button(
            text="Intentar conexión",
            size_hint=(1, 0.1),
            background_color=PRIMARY_COLOR,
            color=TEXT_COLOR
        )
        connect_button.bind(on_press=self.attempt_connection)
        self.add_widget(connect_button)

        # Comando
        command_layout = BoxLayout(size_hint=(1, 0.1), spacing=10)
        command_label = Label(text="Comando:", size_hint=(0.3, 1), color=PRIMARY_COLOR)
        self.command_input = TextInput(multiline=False, size_hint=(0.7, 1))
        command_layout.add_widget(command_label)
        command_layout.add_widget(self.command_input)
        self.add_widget(command_layout)

        # Botón enviar
        send_button = Button(
            text="Enviar",
            size_hint=(1, 0.1),
            background_color=PRIMARY_COLOR,
            color=TEXT_COLOR
        )
        send_button.bind(on_press=self.send_command)
        self.add_widget(send_button)

        # Área de respuesta
        self.response_label = Label(
            text="Respuesta: N/A",
            size_hint=(1, 0.2),
            color=PRIMARY_COLOR
        )
        self.add_widget(self.response_label)

    def attempt_connection(self, instance):
        try:
            port = 0 if self.spi_port_selector.text == "SPI0" else 1
            speed = int(self.speed_input.text)

            if not self.spi_connected:
                self.spi.open(0, port)
                self.spi.max_speed_hz = speed
                self.spi_connected = True
                self.connection_status.text = "Estado: Conectado"
                self.connection_status.color = (0, 1, 0, 1)  # Verde para conectado
                self.log_message("SPI conectado correctamente.")
            else:
                self.spi.close()
                self.spi_connected = False
                self.connection_status.text = "Estado: Desconectado"
                self.connection_status.color = (1, 0, 0, 1)  # Rojo para desconectado
                self.log_message("SPI desconectado.")
        except Exception as e:
            self.spi_connected = False
            self.connection_status.text = "Estado: Desconectado"
            self.connection_status.color = (1, 0, 0, 1)
            self.log_message(f"Error al conectar SPI: {e}")

    def send_command(self, instance):
        command = self.command_input.text
        if not self.spi_connected:
            self.log_message("Error: SPI no está conectado.")
            return

        if not command:
            self.log_message("Error: Comando vacío.")
            return

        try:
            data_to_send = [int(x) for x in command.split(",")]
            response = self.spi.xfer2(data_to_send)
            self.response_label.text = f"Respuesta: {response}"
            self.log_message(f"Enviado: {data_to_send} | Recibido: {response}")
        except Exception as e:
            self.response_label.text = "Error al enviar comando"
            self.log_message(f"Error al enviar comando SPI: {e}")

    def log_message(self, message):
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"{timestamp} - {message}"
        print(formatted_message)
        with open("terminal_log.txt", "a") as log_file:
            log_file.write(formatted_message + "\n")
        if self.terminal_callback:
            self.terminal_callback(formatted_message)
