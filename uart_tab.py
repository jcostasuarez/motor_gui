from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from uart import UARTBackend
from constants import *

class UARTTab(BoxLayout):
    def __init__(self, uart_backend, terminal_callback, uart_label, **kwargs):
        super().__init__(orientation='vertical', spacing=10, padding=10, **kwargs)

        self.backend = uart_backend
        self.terminal_callback = terminal_callback
        self.uart_label = uart_label

        # Indicador de estado de la conexión
        self.connection_status = Label(
            text="Estado: Desconectado",
            size_hint=(1, 0.1),
            color=(1, 0, 0, 1)  # Rojo para desconectado
        )
        self.add_widget(self.connection_status)

        # Selección del puerto UART
        self.add_widget(self._create_uart_selection())

        # Campo para ingresar el baudrate
        self.add_widget(self._create_input_row("Baudrate:", "9600", "baud_input"))

        # Botón para conectar/desconectar UART
        connect_button = Button(
            text="Conectar UART",
            size_hint=(1, 0.1),
            background_color=PRIMARY_COLOR,
            color=TEXT_COLOR
        )
        connect_button.bind(on_press=self.toggle_uart_connection)
        self.add_widget(connect_button)

        # Campo para ingresar comandos
        self.add_widget(self._create_input_row("Comando:", "", "command_input"))

        # Botón para enviar comando
        send_button = Button(
            text="Enviar",
            size_hint=(1, 0.1),
            background_color=PRIMARY_COLOR,
            color=TEXT_COLOR
        )
        send_button.bind(on_press=self.send_command)
        self.add_widget(send_button)

        # Área para mostrar la respuesta recibida
        self.response_label = Label(
            text="Respuesta: N/A",
            size_hint=(1, 0.2),
            color=PRIMARY_COLOR
        )
        self.add_widget(self.response_label)

    def _create_input_row(self, label_text, default_text, attribute_name):
        """Crear un campo de entrada con etiqueta."""
        layout = BoxLayout(size_hint=(1, 0.1), spacing=10)
        label = Label(text=label_text, size_hint=(0.3, 1), color=PRIMARY_COLOR)
        text_input = TextInput(text=default_text, multiline=False, size_hint=(0.7, 1))
        layout.add_widget(label)
        layout.add_widget(text_input)
        setattr(self, attribute_name, text_input)
        return layout

    def _create_uart_selection(self):
        """Crear la selección de puertos UART con botón de actualización."""
        layout = BoxLayout(size_hint=(1, 0.1), spacing=10)
        label = Label(text="Puerto UART:", size_hint=(0.3, 1), color=PRIMARY_COLOR)
        self.port_selector = Spinner(size_hint=(0.5, 1))
        self.update_uart_ports()
        update_button = Button(
            text="Actualizar",
            size_hint=(0.2, 1),
            background_color=PRIMARY_COLOR,
            color=TEXT_COLOR
        )
        update_button.bind(on_press=lambda x: self.update_uart_ports())
        layout.add_widget(label)
        layout.add_widget(self.port_selector)
        layout.add_widget(update_button)
        return layout

    def update_uart_ports(self):
        """Actualizar la lista de puertos UART disponibles."""
        ports = self.backend.update_uart_ports()
        self.port_selector.values = ports if ports else ["No disponible"]
        self.port_selector.text = ports[0] if ports else "No disponible"

    def toggle_uart_connection(self, instance):
        """Conectar o desconectar la interfaz UART."""
        if self.backend.uart_connected:
            self.backend.disconnect()
            self.connection_status.text = "Estado: Desconectado"
            self.connection_status.color = (1, 0, 0, 1)  # Rojo

            self.uart_label.text = "Estado: Desconectado"
            self.uart_label.color = (1, 0, 0, 1)  # Rojo
        else:
            port = self.port_selector.text
            baudrate = int(self.baud_input.text)
            if self.backend.connect(port, baudrate):
                self.connection_status.text = "Estado: Conectado"
                self.connection_status.color = (0, 1, 0, 1)  # Verde

                self.uart_label.text = "Estado: Conectado"
                self.uart_label.color = (0, 1, 0, 1)  # Verde


    def send_command(self, instance):
        """Enviar un comando a través de UART usando send_command_with_response."""
        command = self.command_input.text

        try:
            # Validar entrada del comando
            if not command:
                self.response_label.text = "Error: Comando vacío"
                return

            # Only one byte
            command = ord(command[0])

            # Enviar el comando y obtener la respuesta
            response = self.backend.send_generic_command(command)
            self.response_label.text = f"Respuesta: {response.hex()}" if response else "Error: Sin respuesta"
        except ValueError:
            self.response_label.text = "Error: Entrada no válida"
