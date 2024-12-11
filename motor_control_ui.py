# Archivo: motor_control_ui.py
from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from main_tab import MainTab
from uart_tab import UARTTab
from terminal_tab import TerminalTab
from kivy.core.window import Window

# Paleta de colores basada en la página de la UTN
PRIMARY_COLOR = (0.0, 0.32, 0.63, 1)  # Azul UTN
SECONDARY_COLOR = (0.8, 0.8, 0.8, 1)  # Gris claro
BACKGROUND_COLOR = (1, 1, 1, 1)       # Blanco
TAB_TEXT_COLOR = (1, 1, 1, 1)         # Blanco para texto en pestañas activas
INACTIVE_TAB_COLOR = (0.9, 0.9, 0.9, 1)  # Gris claro para pestañas inactivas

# Ajustar fondo blanco para un diseño más limpio
Window.clearcolor = BACKGROUND_COLOR

class MotorControlPanel(TabbedPanel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Desactivar la pestaña predeterminada
        self.do_default_tab = False

        self.tab_width = 150  # Ancho de las pestañas
        self.tab_height = 50  # Altura de las pestañas
        self.background_color = BACKGROUND_COLOR

        # Pestaña Control
        self.main_tab = TabbedPanelItem(text="Control")
        self.main_tab.background_color = PRIMARY_COLOR
        self.main_tab_content = MainTab(terminal_callback=self.append_terminal_message)
        self.main_tab.add_widget(self.main_tab_content)
        self.add_widget(self.main_tab)

        # Pestaña Terminal
        self.terminal_tab = TabbedPanelItem(text="Terminal")
        self.terminal_tab.background_color = SECONDARY_COLOR
        self.terminal_tab_content = TerminalTab()
        self.terminal_tab.add_widget(self.terminal_tab_content)
        self.add_widget(self.terminal_tab)

        # Sustituye el SPI Tab con UART Tab
        self.uart_tab = TabbedPanelItem(text="UART")
        self.uart_tab_content = UARTTab(terminal_callback=self.append_terminal_message)
        self.uart_tab.add_widget(self.uart_tab_content)
        self.add_widget(self.uart_tab)

    def append_terminal_message(self, message):
        self.terminal_tab_content.append_message(message)

class MotorControlApp(App):
    def build(self):
        return MotorControlPanel()

if __name__ == "__main__":
    MotorControlApp().run()

