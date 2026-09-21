
import json
import math
import random
from collections import deque
from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import (
    Color, Ellipse, Line, Mesh, PopMatrix, PushMatrix, Rectangle,
    RoundedRectangle, Scale, Translate
)
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget


class SoftFlash(Widget):
    """Ambient soft pulse: no sensor, no strobing."""
    alpha = NumericProperty(0.0)
    radius = NumericProperty(0.0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._draw, size=self._draw, alpha=self._draw, radius=self._draw)

    def pulse(self, strength=0.28, duration=0.55):
        self.alpha = strength
        self.radius = max(self.width, self.height) * 0.12
        from kivy.animation import Animation
        Animation.cancel_all(self, "alpha", "radius")
        anim = Animation(alpha=0.0, radius=max(self.width, self.height) * 0.72,
                         duration=duration, t="out_quad")
        anim.start(self)

    def _draw(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            if self.alpha > 0:
                Color(0.55, 0.80, 1.0, self.alpha)
                r = self.radius
                Ellipse(pos=(self.center_x-r, self.center_y-r), size=(2*r, 2*r))


class Die3D(Widget):
    value = NumericProperty(1)
    rot = NumericProperty(0.0)
    scale3d = NumericProperty(1.0)
    squash = NumericProperty(1.0)
    glow = NumericProperty(0.0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.value = 1
        self.bind(pos=self.redraw, size=self.redraw, value=self.redraw,
                  rot=self.redraw, scale3d=self.redraw,
                  squash=self.redraw, glow=self.redraw)
        self.redraw()

    def set_value(self, v):
        self.value = int(max(1, min(6, v)))

    def redraw(self, *_):
        self.canvas.clear()
        w, h = self.size
        if w <= 2 or h <= 2:
            return
        s = min(w, h) * 0.72 * self.scale3d
        x = self.center_x - s / 2
        y = self.center_y - s / 2

        with self.canvas:
            # soft halo
            if self.glow > 0:
                Color(0.35, 0.85, 1.0, 0.10 * self.glow)
                Ellipse(pos=(x-s*0.16, y-s*0.16), size=(s*1.32, s*1.32))

            # top/right extrusion gives a pseudo-3D solid
            depth = s * 0.14
            Color(0.08, 0.11, 0.18, 1)
            RoundedRectangle(pos=(x+depth, y+depth), size=(s, s), radius=[s*0.16])

            Color(0.16, 0.22, 0.34, 1)
            RoundedRectangle(pos=(x, y), size=(s, s), radius=[s*0.16])

            # glass/neon face
            Color(0.16, 0.55, 0.78, 0.30 + 0.08*self.glow)
            RoundedRectangle(pos=(x+s*0.035, y+s*0.035),
                             size=(s*0.93, s*0.93), radius=[s*0.14])

            # face border
            Color(0.40, 0.92, 1.0, 0.78)
            Line(rounded_rectangle=(x, y, s, s, s*0.16), width=1.4)

            self._pips(x, y, s)

    def _pips(self, x, y, s):
        patterns = {
            1: [(0,0)],
            2: [(-1,1),(1,-1)],
            3: [(-1,1),(0,0),(1,-1)],
            4: [(-1,1),(1,1),(-1,-1),(1,-1)],
            5: [(-1,1),(1,1),(0,0),(-1,-1),(1,-1)],
            6: [(-1,1),(-1,0),(-1,-1),(1,1),(1,0),(1,-1)]
        }
        r = s * 0.075
        for px, py in patterns[self.value]:
            cx = x + s*(0.5 + px*0.22)
            cy = y + s*(0.5 + py*0.22)
            Color(0.82, 0.98, 1.0, 0.88)
            Ellipse(pos=(cx-r, cy-r), size=(2*r, 2*r))
            Color(1, 1, 1, 0.22)
            Ellipse(pos=(cx-r*0.35, cy+r*0.05), size=(r*0.55, r*0.55))


class BlochView(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theta = 0.0
        self.phi = 0.0
        self.bind(pos=self.draw, size=self.draw)
        Clock.schedule_interval(self.animate, 1/30)

    def animate(self, dt):
        self.theta += dt * 0.8
        self.phi += dt * 0.35
        self.draw()

    def draw(self, *_):
        self.canvas.clear()
        cx, cy = self.center
        r = min(self.width, self.height) * 0.27
        with self.canvas:
            Color(0.25, 0.85, 1.0, 0.16)
            Ellipse(pos=(cx-r, cy-r), size=(2*r, 2*r))
            Color(0.35, 0.90, 1.0, 0.60)
            Line(circle=(cx, cy, r), width=1.1)
            Line(points=[cx-r,cy,cx+r,cy], width=0.8)
            Line(points=[cx,cy-r,cx,cy+r], width=0.8)

            # two conceptual qubit state vectors
            for phase, length, color in [
                (self.theta, r*0.86, (0.35, 1.0, 0.72)),
                (self.phi, r*0.70, (1.0, 0.48, 0.78))
            ]:
                ex = cx + math.cos(phase) * length
                ey = cy + math.sin(phase) * length * 0.65
                Color(*color, 0.85)
                Line(points=[cx,cy,ex,ey], width=2.0)
                Color(*color, 1)
                Ellipse(pos=(ex-4,ey-4), size=(8,8))


class DiceTable(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.draw, size=self.draw)

    def draw(self, *_):
        self.canvas.clear()
        with self.canvas:
            Color(0.025,0.035,0.06,1)
            Rectangle(pos=self.pos, size=self.size)
            Color(0.08,0.20,0.28,0.35)
            step = max(35, min(self.width,self.height)/8)
            for xx in range(int(self.x), int(self.right)+1, int(step)):
                Line(points=[xx,self.y,xx,self.top], width=0.5)
            for yy in range(int(self.y), int(self.top)+1, int(step)):
                Line(points=[self.x,yy,self.right,yy], width=0.5)
            Color(0.20,0.75,0.95,0.08)
            Ellipse(pos=(self.x+self.width*.18,self.y+self.height*.10),
                    size=(self.width*.64,self.height*.28))


class QuantumOracleDiceApp(App):
    title_text = StringProperty("QUANTUM ORACLE DICE")
    mode = StringProperty("JUSTO")
    result_text = StringProperty("Listo para lanzar")

    def build(self):
        self.history_file = Path(self.user_data_dir) / "historia_oraculo.json"
        self.history = self._load_history()
        self.running = False
        self.flash = SoftFlash()
        self.dice_area = DiceTable()
        self.d1 = Die3D()
        self.d2 = Die3D()
        self.dice_area.add_widget(self.d1)
        self.dice_area.add_widget(self.d2)

        root = BoxLayout(orientation="vertical", padding=8, spacing=6)
        header = BoxLayout(size_hint_y=None, height=48)
        header.add_widget(Label(text=self.title_text, font_size="19sp",
                                bold=True, color=(0.55,0.9,1,1)))
        self.mode_btn = Button(text="MODO: JUSTO", size_hint_x=None, width=135)
        self.mode_btn.bind(on_release=self.change_mode)
        header.add_widget(self.mode_btn)
        root.add_widget(header)

        root.add_widget(self.dice_area)
        self.flash.size = self.dice_area.size
        self.flash.pos = self.dice_area.pos
        self.dice_area.add_widget(self.flash)

        lower = BoxLayout(size_hint_y=None, height=170, spacing=6)
        self.bloch = BlochView(size_hint_x=0.38)
        lower.add_widget(self.bloch)

        info = BoxLayout(orientation="vertical", spacing=4)
        self.result = Label(text=self.result_text, font_size="22sp",
                            color=(0.85,0.95,1,1))
        self.detail = Label(text="2 dados · 2 qubits conceptuales · sin sensor",
                            font_size="13sp")
        info.add_widget(self.result)
        info.add_widget(self.detail)

        buttons = BoxLayout(size_hint_y=None, height=52, spacing=5)
        launch = Button(text="LANZAR", font_size="18sp")
        launch.bind(on_release=self.launch)
        hist = Button(text="HISTORIA")
        hist.bind(on_release=self.show_history)
        buttons.add_widget(launch)
        buttons.add_widget(hist)
        info.add_widget(buttons)
        lower.add_widget(info)
        root.add_widget(lower)
        return root

    def _load_history(self):
        try:
            if self.history_file.exists():
                return json.loads(self.history_file.read_text(encoding="utf-8"))
        except Exception:
            pass
        return []

    def _save_history(self):
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self.history_file.write_text(
            json.dumps(self.history[-100:], ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    def change_mode(self, *_):
        modes = ["JUSTO", "CAOS", "ORACULO"]
        self.mode = modes[(modes.index(self.mode)+1) % len(modes)]
        self.mode_btn.text = "MODO: " + self.mode
        self.detail.text = f"Modo {self.mode} · sin sensor · destellos suaves"

    def launch(self, *_):
        if self.running:
            return
        self.running = True
        self.result.text = "Los dados están en movimiento…"
        self.detail.text = "Animación procedural 3D"
        self.flash.pulse(0.16, 0.45)

        # Choose final values according to the selected game mode.
        if self.mode == "JUSTO":
            a, b = random.randint(1,6), random.randint(1,6)
        elif self.mode == "CAOS":
            a = random.randint(1,6)
            b = random.choice([1,2,3,4,5,6])
        else:
            # Oracle mode is deterministic from a Bell-like conceptual state,
            # but remains a game abstraction rather than a physical quantum die.
            pair = random.choice([(1,6),(2,5),(3,4),(4,3),(5,2),(6,1)])
            a, b = pair

        self.target1, self.target2 = a, b
        self.t = 0.0
        self.phase = 0
        Clock.schedule_interval(self._animate_roll, 1/60)

    def _animate_roll(self, dt):
        self.t += dt
        self.phase += 1
        self.d1.rot += 20 + random.random()*14
        self.d2.rot -= 17 + random.random()*15
        self.d1.scale3d = 1.0 + 0.08*math.sin(self.t*20)
        self.d2.scale3d = 1.0 + 0.08*math.sin(self.t*21+1)

        if self.phase % 9 == 0:
            self.d1.set_value(random.randint(1,6))
            self.d2.set_value(random.randint(1,6))
        if self.phase % 18 == 0:
            self.flash.pulse(0.08, 0.22)

        # End after ~1.8 s.
        if self.t >= 1.8:
            return self._finish_roll()

    def _finish_roll(self):
        try:
            self.d1.set_value(self.target1)
            self.d2.set_value(self.target2)
            self.d1.rot = self.d2.rot = 0
            self.d1.scale3d = self.d2.scale3d = 1
            self.flash.pulse(0.28, 0.80)
            total = self.target1 + self.target2
            self.result.text = f"{self.target1} + {self.target2} = {total}"
            self.detail.text = (
                f"Resultado {self.mode} · estado conceptual: "
                f"|{self.target1-1},{self.target2-1}⟩"
            )
            self.history.append({
                "dice": [self.target1, self.target2],
                "total": total,
                "mode": self.mode,
                "state": f"|{self.target1-1},{self.target2-1}>",
                "timestamp": __import__("datetime").datetime.now().isoformat()
            })
            self._save_history()
        finally:
            self.running = False
            return False

    def show_history(self, *_):
        if not self.history:
            self.result.text = "Sin lanzamientos guardados"
            return
        recent = self.history[-5:]
        lines = [f"{i+1}. {x['dice'][0]} + {x['dice'][1]} = {x['total']} · {x['mode']}"
                 for i, x in enumerate(recent)]
        self.result.text = "\n".join(lines)
        self.detail.text = "Últimos 5 lanzamientos guardados localmente"


if __name__ == "__main__":
    QuantumOracleDiceApp().run()
