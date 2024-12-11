import serial
from serial.tools import list_ports

class UARTBackend:
    def __init__(self, terminal_callback=None):
        self.terminal_callback = terminal_callback
        self.uart_connected = False
        self.serial_port = None

    def update_uart_ports(self):
        """Obtener la lista de puertos UART disponibles."""
        try:
            return [port.device for port in list_ports.comports()]
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

    def send_command_with_response(self, command_id, value=None):
        """
        Enviar un comando en formato 'xy' y recibir la respuesta.
        - command_id: Identificador del comando (x) (1 byte).
        - value: Variable asociada al comando (y), puede ser None, uint8_t o int32_t.
        """
        if not self.uart_connected:
            self.log_message("Error: UART no está conectado.")
            return None

        try:
            # Preparar el mensaje
            if value is None:
                message = f"{command_id:02X}"  # Solo el comando
            elif isinstance(value, int):
                if 0 <= value <= 0xFF:  # uint8_t
                    message = f"{command_id:02X}{value:02X}"
                elif -0x80000000 <= value <= 0x7FFFFFFF:  # int32_t
                    message = f"{command_id:02X}{value:08X}"
                else:
                    raise ValueError("El valor debe ser uint8_t o int32_t.")
            else:
                raise TypeError("El valor debe ser un entero (uint8_t o int32_t).")

            # Enviar el comando
            response = self.send_command(message)

            # Procesar la respuesta
            if response:
                self.log_message(f"Respuesta recibida: {response}")
                return response
            else:
                self.log_message("No se recibió respuesta.")
                return None
        except Exception as e:
            self.log_message(f"Error al enviar comando: {e}")
            return None

    def send_command(self, command, size=4):
        """
        Enviar un comando a través de UART y obtener la respuesta.
        """
        if not self.uart_connected:
            self.log_message("Error: UART no está conectado.")
            return None

        try:
            # Enviar comando
            self.serial_port.write(command.encode())
            response = self.serial_port.read_until(size=size)
            self.log_message(f"Enviado: {command} | Recibido: {response}")
            return response
        except Exception as e:
            self.log_message(f"Error al enviar comando UART: {e}")
            return None

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
