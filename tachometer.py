# Archivo: tachometer.py
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line, Mesh
import math

class Tachometer(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.configured_value = 0  # RPM value set by the user
        self.real_value = 0       # Real RPM value received from a signal
        self.max_rpm = 100        # Maximum RPM (linked to the slider max value)
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.canvas.clear()
        radius = min(self.width, self.height) / 2
        center_x, center_y = self.center

        with self.canvas:
            # Draw background circle
            Color(0.2, 0.2, 0.2, 1)
            Ellipse(pos=(center_x - radius, center_y - radius), size=(2 * radius, 2 * radius))

            # Draw RPM markers
            for rpm in range(0, self.max_rpm + 1, 10):
                angle = -90 + (360 * rpm / self.max_rpm)  # Start at the top (-90 degrees) and move clockwise
                radian = math.radians(angle)

                # Calculate marker positions
                x_outer = center_x + radius * math.cos(radian)
                y_outer = center_y + radius * math.sin(radian)
                x_inner = center_x + (radius - 20) * math.cos(radian)
                y_inner = center_y + (radius - 20) * math.sin(radian)
                Color(1, 1, 1, 1)
                Line(points=[x_outer, y_outer, x_inner, y_inner], width=1)

            # Draw real value fill (semi-transparent blue)
            Color(0, 0, 1, 0.5)
            step = 1
            points = [center_x, center_y]
            for rpm in range(0, int(self.real_value) + step, step):
                angle = -90 + (360 * rpm / self.max_rpm)
                radian = math.radians(angle)
                x = center_x + radius * math.cos(radian)
                y = center_y + radius * math.sin(radian)
                points.extend([x, y])
            Mesh(vertices=points, indices=list(range(len(points) // 2)), mode="triangle_fan")

            # Draw configured value needle (blue)
            Color(0, 0, 1, 1)
            angle_configured = -90 + (360 * self.configured_value / self.max_rpm)
            radian_configured = math.radians(angle_configured)
            x_configured = center_x + (radius - 20) * math.cos(radian_configured)
            y_configured = center_y + (radius - 20) * math.sin(radian_configured)
            Line(points=[center_x, center_y, x_configured, y_configured], width=2)

    def set_configured_value(self, value):
        self.configured_value = value
        self.update_canvas()

    def set_real_value(self, value):
        self.real_value = value
        self.update_canvas()

    def set_max_rpm(self, max_rpm):
        self.max_rpm = max_rpm
        self.update_canvas()
