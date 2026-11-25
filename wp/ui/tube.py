"""The horizontal glass tube of a resource (package 33, UI_WISHES "Classic screen v2" points 3 and 5).

Tube(resource) is a QWidget painted with QPainter: the glass body (token tube_glass), the empty part (tube_empty),
the liquid (the resource token as a gradient), the highlight (tube_highlight, strength tube_gloss), the segment ticks
(tube_segment, every `step` points: app setting resource_segments) and, for HP, the temporary HP strip (token
temp_hp) along the bottom third, segmented by 5 points, that may be longer than the HP fill.
Style "flat" paints the same geometry without gradient and highlight (size, value and logic unchanged).
Mode "thin" (auto-switch) paints a thin bar with the number inside. A click emits `clicked` (the value editor).
Numbers come from tube_logic (no game logic here); colours from the theme tokens the window gives (colors dict).
"""
import re

from PySide6.QtCore import QRectF, QSize, Qt, Signal
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPen
from PySide6.QtWidgets import QSizePolicy, QWidget

from wp.ui import tube_logic as tl

_RGBA = re.compile(r"rgba\((\d+),\s*(\d+),\s*(\d+),\s*(\d+)\)")
GLASS, FLAT = "glass", "flat"
PCT = 100.0                            # tube_gloss is a percent
ALPHA_MAX = 255
TEMP_PART = 3                          # the temp HP strip = the bottom third (UI_WISHES point 5)
LIGHTER, DARKER = 135, 125             # the liquid gradient (QColor.lighter / darker factors)
EDGE = 0.5                             # half a pixel: crisp 1 px outlines
HALF = 2.0                             # a rounded end = half the height
RADIUS = 4                             # the corner radius when the theme gives none
GLOSS = 50                             # the highlight strength when the theme gives none (percent)
GLOSS_INSET = 2                        # the highlight band: inset from the ends (px)
GLOSS_PART = 3.0                       # the highlight band = the top third


def color(value, default="#808080"):
    """A QColor from a token text: #rrggbb, or rgba(r, g, b, a) (qss.qt_color of #rrggbbaa)."""
    v = str(value or default)
    m = _RGBA.match(v)
    if m:
        return QColor(*[int(x) for x in m.groups()])
    c = QColor(v)
    return c if c.isValid() else QColor(default)


class Tube(QWidget):
    clicked = Signal(str)

    def __init__(self, resource, token):
        super().__init__()
        self.resource, self.token = resource, token
        self.current, self.maximum, self.temp, self.step, self.temp_step = 0, 0, 0, 0, 0
        self.style_name, self.mode, self.colors = GLASS, "big", {}
        self.wanted = QSize(1, 1)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setCursor(Qt.PointingHandCursor)

    # ------------------------------------------------------------ state from the block
    def set_values(self, current, maximum, temp=0, step=0, temp_step=0):
        self.current, self.maximum, self.temp = int(current), int(maximum or 0), int(temp or 0)
        self.step, self.temp_step = int(step or 0), int(temp_step or 0)
        self.update()

    def set_look(self, style_name, mode, colors, width, height):
        self.style_name, self.mode, self.colors = style_name, mode, dict(colors)
        self.wanted = QSize(int(width), int(height))
        self.setMaximumWidth(int(width))
        self.setFixedHeight(max(1, int(height)))
        self.update()

    def sizeHint(self):
        return self.wanted

    def fill(self):
        return tl.fill(self.current, self.maximum)

    def text(self):
        return "%d / %d" % (self.current, self.maximum)

    # ------------------------------------------------------------ painting
    def _c(self, key):
        return color(self.colors.get(key))

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        r = QRectF(self.rect()).adjusted(EDGE, EDGE, -EDGE, -EDGE)
        radius = min(r.height() / HALF, float(self.colors.get("radius", RADIUS) or 0))
        p.setPen(Qt.NoPen)
        p.setBrush(self._c("tube_empty"))
        p.drawRoundedRect(r, radius, radius)
        liquid = QRectF(r.x(), r.y(), r.width() * self.fill(), r.height())
        base = self._c(self.token)
        if self.style_name == GLASS and self.mode != "thin":
            g = QLinearGradient(liquid.topLeft(), liquid.bottomLeft())
            g.setColorAt(0.0, base.lighter(LIGHTER))
            g.setColorAt(1.0, base.darker(DARKER))
            p.setBrush(g)
        else:
            p.setBrush(base)
        if liquid.width() > 0:
            p.drawRoundedRect(liquid, radius, radius)
        if self.temp > 0:
            self._temp_strip(p, r)
        p.setPen(QPen(self._c("tube_segment"), 1))
        for x in tl.ticks(self.maximum, self.step):
            xx = r.x() + r.width() * x
            p.drawLine(int(xx), int(r.top() + 1), int(xx), int(r.bottom() - 1))
        if self.style_name == GLASS and self.mode != "thin":
            hi = self._c("tube_highlight")
            hi.setAlpha(int(ALPHA_MAX * float(self.colors.get("tube_gloss", GLOSS) or 0) / PCT))
            p.setPen(Qt.NoPen)
            p.setBrush(hi)
            band = QRectF(r.x() + GLOSS_INSET, r.y() + 1, r.width() - HALF * GLOSS_INSET, r.height() / GLOSS_PART)
            p.drawRoundedRect(band, radius, radius)
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(self._c("tube_glass"), 1))
        p.drawRoundedRect(r, radius, radius)
        if self.mode == "thin":
            over = tl.over_max(self.current, self.maximum)
            p.setPen(self._c("warning" if over else "text"))
            p.drawText(r, Qt.AlignCenter, self.text())
        p.end()

    def _temp_strip(self, p, r):
        h = r.height() / TEMP_PART
        strip = QRectF(r.x(), r.bottom() - h, r.width() * tl.temp_fill(self.temp, self.maximum), h)
        p.setPen(Qt.NoPen)
        p.setBrush(self._c("temp_hp"))
        p.drawRect(strip)
        p.setPen(QPen(self._c("tube_segment"), 1))
        for x in tl.ticks(self.maximum, self.temp_step):
            xx = r.x() + r.width() * x
            if xx <= strip.right():
                p.drawLine(int(xx), int(strip.top()), int(xx), int(strip.bottom()))

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.resource)
        super().mouseReleaseEvent(event)
