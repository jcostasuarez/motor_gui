import serial
from serial.tools import list_ports
from time import sleep
from constants import *

class UARTBackend:
    def __init__(self, terminal_callback=None):
        self.terminal_callback = terminal_callback
        self.uart_connected = False
        self.serial_port = None

    def update_uart_ports(self):
        """Obtener la lista de puertos UART disponibles."""
        try:
            display_ports = []
            for port in list_ports.comports():
                if ("USB" in port.device or "ACM" in port.device):
                    display_ports.append(port.device)
            return display_ports
        except Exception as e:
            self.log_message(f"Error al actualizar puertos UART: {e}")
            return []

    def connect(self, port, baudrate):
        """Conectar al puerto UART."""
        if self.uart_connected:
            self.disconnect()
        try:
            self.serial_port = serial.Serial(port, baudrate, timeout=1)
            self.uart_connected = True
            self.log_message("UART conectado correctamente.")

            return True
        except Exception as e:
            self.log_message(f"Error al conectar UART: {e}")
            return False

    def disconnect(self):
        """Desconectar UART."""
        if self.serial_port:
            self.serial_port.close()
        self.uart_connected = False
        self.log_message("UART desconectado.")

    def read_line(self):
        if (self.serial_port):
            return self.serial_port.readline()


    def get_speed(self):
        if not self.uart_connected:
            self.log_message("Error: UART no está conectado.")
            return None

        try:
            # Construir el mensaje
            message = bytearray([CMD_GET_SPEED])  # Comando en 1 byte

            # Clean UART buffer
            self.serial_port.write(message)
            self.serial_port.flush()
            response = self.serial_port.read_until(size=1)

            return response

        except Exception as e:
            self.log_message(f"Error al enviar comando: {e}")
            return None

    def set_speed(self, value):
        if not self.uart_connected:
            self.log_message("Error: UART no está conectado.")
            return None

        # Reverse duty, weird bug
        message = bytearray([CMD_SET_SPEED])  # Comando en 1 byte
        value = bytearray([value])

        self.serial_port.write(message)
        self.serial_port.flush()
        sleep(0.1)
        self.serial_port.write(value)
        self.serial_port.flush()
        response = self.serial_port.read_until(size=1)


    def turn_on_motor(self, state:bool):
        if not self.uart_connected:
            self.log_message("Error: UART no está conectado.")
            return None

        message = bytearray([CMD_MOTOR_ON_OFF])  # Comando en 1 byte
        value = bytearray([state])

        self.serial_port.write(message)
        self.serial_port.flush()
        sleep(0.1)
        self.serial_port.write(value)
        self.serial_port.flush()
        response = self.serial_port.read_until(size=1)

    def send_generic_command(self, command):
        if not self.uart_connected:
            self.log_message("Error: UART no está conectado.")
            return None

        message = bytearray([command])  # Comando en 1 byte

        self.serial_port.write(message)
        self.serial_port.flush()
        sleep(0.1)
        response = self.serial_port.read_all()
        return response

    def get_current(self):
        if not self.uart_connected:
            self.log_message("Error: UART no está conectado.")
            return None

        message = bytearray([CMD_GET_C2])  # Comando en 1 byte

        self.serial_port.write(message)
        self.serial_port.flush()
        sleep(0.1)
        response = self.serial_port.read_all()
        return response


    def log_message(self, message):
        """
        Registrar un mensaje en el terminal interno.
        """
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"{timestamp} - {message}"
        print(formatted_message)
        if self.terminal_callback:
            self.terminal_callback(formatted_message)
