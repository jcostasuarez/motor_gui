# Archivo: terminal_tab.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput

class TerminalTab(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.terminal_output = TextInput(
            readonly=True,
            multiline=True,
            size_hint=(1, 1),
            font_size=14
        )
        self.add_widget(self.terminal_output)

    def append_message(self, message):
        self.terminal_output.text += f"{message}\n"