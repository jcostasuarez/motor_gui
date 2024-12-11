# Archivo: main_tab.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.clock import Clock

from uart import UARTBackend
from tachometer import Tachometer


# Paleta de colores basada en motor_control_ui.py
PRIMARY_COLOR = (0.0, 0.32, 0.63, 1)  # Azul UTN
SECONDARY_COLOR = (0.8, 0.8, 0.8, 1)  # Gris claro
TEXT_COLOR = (1, 1, 1, 1)             # Blanco

class MainTab(BoxLayout):
    def __init__(self, terminal_callback, **kwargs):
        super().__init__(orientation='vertical', spacing=10, padding=10, **kwargs)

        self.uart_backend = UARTBackend(terminal_callback)
        self.terminal_callback = terminal_callback
        
        # Tacómetro
        self.tachometer = Tachometer(size_hint=(1, 0.5))
        self.add_widget(self.tachometer)

        # Separador
        self.add_widget(Widget(size_hint_y=0.02))

        # Indicador de estado de UART
        self.uart_status = Label(
            text="UART: Desconectado",
            size_hint=(1, 0.1),
            color=(1, 0, 0, 1)  # Rojo para desconectado
        )
        self.add_widget(self.uart_status)

        # Separador
        self.add_widget(Widget(size_hint_y=0.02))

        # Selector de modo
        mode_layout = BoxLayout(size_hint=(1, 0.1), orientation='horizontal', spacing=10)
        mode_label = Label(text="Modo:", size_hint=(0.3, 1), color=PRIMARY_COLOR)
        self.mode_selector = Spinner(
            text="Normal",
            values=("Normal", "Velocidad constante", "Torque constante", "Trapezoidal", "FOC"),
            size_hint=(0.7, 1),
            background_color=PRIMARY_COLOR,
            color=TEXT_COLOR
        )
        self.mode_selector.bind(text=self.set_mode)
        mode_layout.add_widget(mode_label)
        mode_layout.add_widget(self.mode_selector)
        self.add_widget(mode_layout)

        # Separador
        self.add_widget(Widget(size_hint_y=0.02))

        # Control de velocidad
        self.speed_slider = Slider(min=0, max=100, value=0, size_hint=(1, 0.2))
        self.speed_slider.bind(value=self.update_speed)
        self.add_widget(self.speed_slider)

        self.speed_label = Label(text="Velocidad: 0 RPM", size_hint=(1, 0.1), color=PRIMARY_COLOR)
        self.add_widget(self.speed_label)

        # Separador
        self.add_widget(Widget(size_hint_y=0.02))

        # Botones de control
        control_layout = BoxLayout(size_hint=(1, 0.1), spacing=10)
        self.start_button = Button(
            text="Iniciar Motor",
            size_hint=(0.5, 1),
            background_color=PRIMARY_COLOR,
            color=TEXT_COLOR
        )
        self.start_button.bind(on_press=self.start_motor)
        control_layout.add_widget(self.start_button)

        self.stop_button = Button(
            text="Detener Motor",
            size_hint=(0.5, 1),
            background_color=SECONDARY_COLOR,
            color=PRIMARY_COLOR
        )
        self.stop_button.bind(on_press=self.stop_motor)
        control_layout.add_widget(self.stop_button)

        self.add_widget(control_layout)

        # Iniciar actualización periódica del tacómetro
        Clock.schedule_interval(self.update_real_speed, 0.1)

    def update_speed(self, instance, value):
        rpm = int(value)
        self.speed_label.text = f"Velocidad: {rpm} RPM"
        self.tachometer.set_configured_value(value)

        if self.uart_backend.uart_connected:
            self.uart_backend.send_command_with_response(2, rpm)  # SET_SPEED:X
        else:
            self.log_message("UART desconectada: no se puede enviar la velocidad.")

    def update_real_speed(self, dt):
        if self.uart_backend.uart_connected:
            response = self.uart_backend.send_command_with_response(5)  # GET_SPEED
            if response:
                try:
                    real_speed = int(response)
                    self.tachometer.set_real_value(real_speed)
                except ValueError:
                    self.log_message("Error al interpretar la respuesta de GET_SPEED.")
        else:
            self.uart_status.text = "UART: Desconectado"
            self.uart_status.color = (1, 0, 0, 1)  # Rojo

    def start_motor(self, instance):
        if self.uart_backend.uart_connected:
            self.uart_backend.send_command_with_response(3, 1)  # MOTOR: ON
            self.log_message("Motor iniciado")
        else:
            self.log_message("UART desconectada: no se puede iniciar el motor.")

    def stop_motor(self, instance):
        if self.uart_backend.uart_connected:
            self.uart_backend.send_command_with_response(3, 0)  # MOTOR: OFF
            self.log_message("Motor detenido")
            self.speed_slider.value = 0  # Reset slider to 0
            self.update_speed(None, 0)  # Update speed to 0
        else:
            self.log_message("UART desconectada: no se puede detener el motor.")

    def set_mode(self, instance, mode):
        if self.uart_backend.uart_connected:
            mode_value = {
                "Normal": 0,
                "Velocidad constante": 1,
                "Torque constante": 2,
                "Trapezoidal": 3,
                "FOC": 4
            }.get(mode, 0)
            self.uart_backend.send_command_with_response(16, mode_value)  # SET_MODE:X
            self.log_message(f"Modo configurado: {mode}")
        else:
            self.log_message("UART desconectada: no se puede configurar el modo.")


    def log_message(self, message):
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"{timestamp} - {message}"
        print(formatted_message)
        with open("terminal_log.txt", "a") as log_file:
            log_file.write(formatted_message + "\n")
        if self.terminal_callback:
            self.terminal_callback(formatted_message)


