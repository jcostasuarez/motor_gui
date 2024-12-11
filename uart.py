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
        Enviar un comando y, si se proporciona, un valor asociado de 1 byte. 
        Espera siempre una respuesta de 4 bytes.
        - command_id: Identificador del comando (1 byte).
        - value: Valor asociado al comando (1 byte), opcional.
        """
        if not self.uart_connected:
            self.log_message("Error: UART no está conectado.")
            return None

        try:
            # Construir el mensaje
            message = bytearray([command_id])  # Comando en 1 byte
            if value is not None:
                if 0 <= value <= 0xFF:  # Asegurar que el valor sea de 1 byte
                    message.append(value)
                else:
                    raise ValueError("El valor debe estar entre 0 y 255 (1 byte).")

            # Enviar el comando directamente
            self.serial_port.write(message)
            self.log_message(f"Comando enviado: {message.hex()}")

            # Leer la respuesta (esperar siempre 4 bytes)
            response = self.serial_port.read_until(size=4)
            if len(response) != 4:
                self.log_message(f"Respuesta incompleta: se esperaban 4 bytes, se recibieron {len(response)} bytes.")
                return None

            self.log_message(f"Respuesta recibida: {response.hex()}")
            return response

        except Exception as e:
            self.log_message(f"Error al enviar comando: {e}")
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
