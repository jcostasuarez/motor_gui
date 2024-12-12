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
from constants import *

class MainTab(BoxLayout):
    def __init__(self, uart_backend, terminal_callback, **kwargs):
        super().__init__(orientation='vertical', spacing=10, padding=10, **kwargs)

        self.uart_backend = uart_backend
        self.terminal_callback = terminal_callback
        self.rpm = 1
        self.last_real_speed = 0
        self.current = 0

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

        # Control de velocidad
        self.speed_slider = Slider(min=1, max=100, value=0, size_hint=(1, 0.2))
        self.speed_slider.bind(value=self.update_speed)
        self.add_widget(self.speed_slider)

        self.speed_label = Label(text="Duty Deseado: 1%", size_hint=(1, 0.1), color=PRIMARY_COLOR)
        self.add_widget(self.speed_label)

        # Separador
        self.add_widget(Widget(size_hint_y=0.02))

        self.current_label = Label(text=f"Duty: {self.current}%", size_hint=(1, 0.1))
        self.add_widget(self.current_label)

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
        Clock.schedule_interval(self.update_real_speed, 2)


    def get_uart_label(self):
        return self.uart_status

    def update_speed(self, instance, value):
        self.rpm = int(value)
        self.speed_label.text = f"Duty Deseado: {self.rpm}%"
        self.tachometer.set_configured_value(value)

    def update_real_speed(self, dt):
        if self.uart_backend.uart_connected:
            response = self.uart_backend.get_speed()  # GET_SPEED
            if response:
                try:
                    real_speed = response[0]
                    print(real_speed)
                    self.tachometer.set_real_value(real_speed)
                    self.last_real_speed = real_speed
                except ValueError:
                    self.log_message("Error al interpretar la respuesta de GET_SPEED.")

            self.uart_backend.set_speed(self.rpm)

            self.current = self.uart_backend.get_current()
            if (self.current != b''):
                self.current_label.text = f"Duty: {float(int.from_bytes(self.current, byteorder='little'))/8}%"

        else:
            self.uart_status.text = "UART: Desconectado"
            self.uart_status.color = (1, 0, 0, 1)  # Rojo


    def start_motor(self, instance):
        if self.uart_backend.uart_connected:
            self.uart_backend.turn_on_motor(True)  # MOTOR: ON
            self.log_message("Motor iniciado")
        else:
            self.log_message("UART desconectada: no se puede iniciar el motor.")

    def stop_motor(self, instance):
        if self.uart_backend.uart_connected:
            self.uart_backend.turn_on_motor(False)  # MOTOR: OFF
            self.log_message("Motor detenido")
            self.speed_slider.value = 0  # Reset slider to 0
            self.update_speed(None, 0)  # Update speed to 0
        else:
            self.log_message("UART desconectada: no se puede detener el motor.")

    def log_message(self, message):
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"{timestamp} - {message}"
        print(formatted_message)
        with open("terminal_log.txt", "a") as log_file:
            log_file.write(formatted_message + "\n")
        if self.terminal_callback:
            self.terminal_callback(formatted_message)


