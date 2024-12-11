from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder

Builder.load_file('layout.kv')

class MotorControlLayout(BoxLayout):
    pass

class PreviewApp(App):
    def build(self):
        return MotorControlLayout()

if __name__ == '__main__':
    PreviewApp().run()