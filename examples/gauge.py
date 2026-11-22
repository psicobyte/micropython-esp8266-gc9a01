# Circular gauge showing the board's ADC pin reading.
#
# Shows: fill_arc(), line(), write() with a proportional font, text() and
# rotation=. Only the part of the arc that changes is redrawn, so no flicker.
#
# Connect a potentiometer to the ADC pin on the header. If the ADC reads 0 at
# startup, a demo mode sweeps the gauge on its own.
# Note: the ESP8266 ADC accepts 0-1 V at the chip; check whether your board has
# a voltage divider before feeding it 3.3 V.
#   mpremote run examples/gauge.py
import math
import time

import machine
import gc9a01
import round_lcd
import vga1_8x16 as small
import NotoSans_32 as noto

# Change ROTATION (0-3) to rotate the whole drawing 90 degrees each step
ROTATION = 0

R_OUTER, R_INNER = 112, 90       # ring radii
START_ANGLE, SWEEP = 135, 270    # starts bottom-left, sweeps 270 degrees clockwise
TRACK = gc9a01.color565(40, 40, 40)
BACKGROUND = gc9a01.BLACK
# zones (from %, to %, colour)
ZONES = (
    (0, 60, gc9a01.GREEN),
    (60, 85, gc9a01.YELLOW),
    (85, 100, gc9a01.RED),
)

tft = round_lcd.display(rotation=ROTATION)
CX, CY = round_lcd.WIDTH // 2, round_lcd.HEIGHT // 2
adc = machine.ADC(0)


def angle(percent):
    return START_ANGLE + percent * SWEEP // 100


def paint_ring(p0, p1, lit):
    """Paint the ring between p0% and p1% (lit = zone colour, otherwise track colour)."""
    if p0 == p1:
        return
    lo, hi = min(p0, p1), max(p0, p1)
    for z0, z1, color in ZONES:
        a, b = max(lo, z0), min(hi, z1)
        if a < b:
            segments = max(1, (b - a) // 2)
            tft.fill_arc(CX, CY, angle(a), angle(b), segments, R_OUTER, R_OUTER,
                         color if lit else TRACK)
    # fill_arc draws a pie slice: cover the centre to leave only the ring
    tft.fill_arc(CX, CY, angle(lo) - 2, angle(hi) + 2, max(1, (hi - lo) // 2),
                 R_INNER, R_INNER, BACKGROUND)


def draw_background():
    tft.fill(BACKGROUND)
    paint_ring(0, 100, False)
    for p in range(0, 101, 10):  # tick marks every 10 %
        a = math.radians(angle(p))
        c, s = math.cos(a), math.sin(a)
        tft.line(int(CX + 114 * c), int(CY + 114 * s),
                 int(CX + 119 * c), int(CY + 119 * s), gc9a01.WHITE)
    tft.text(small, "0", CX - 62, CY + 82, gc9a01.WHITE, BACKGROUND)
    tft.text(small, "100", CX + 42, CY + 82, gc9a01.WHITE, BACKGROUND)


class Label:
    """Centred text that is rewritten without leftovers when its width changes."""

    def __init__(self, y, font, color, proportional):
        self.y, self.font, self.color, self.proportional = y, font, color, proportional
        self.x = self.w = 0

    def __call__(self, txt):
        if self.proportional:
            w = tft.write_len(self.font, txt)
        else:
            w = len(txt) * self.font.WIDTH
        x = CX - w // 2
        h = self.font.HEIGHT
        if self.proportional:
            tft.write(self.font, txt, x, self.y, self.color, BACKGROUND)
        else:
            tft.text(self.font, txt, x, self.y, self.color, BACKGROUND)
        # clear whatever stuck out from the previous text
        if self.w and x > self.x:
            tft.fill_rect(self.x, self.y, x - self.x, h, BACKGROUND)
        if self.w and self.x + self.w > x + w:
            tft.fill_rect(x + w, self.y, self.x + self.w - x - w, h, BACKGROUND)
        self.x, self.w = x, w


def main():
    draw_background()
    value_label = Label(CY - 22, noto, gc9a01.WHITE, True)
    raw_label = Label(CY + 20, small, gc9a01.color565(150, 150, 150), False)
    title_label = Label(CY - 50, small, gc9a01.CYAN, False)

    current = 0
    average = adc.read()
    first = True
    demo = average < 5
    if demo:
        print("ADC reads 0: demo mode (connect a potentiometer to the ADC pin)")
    t0 = time.ticks_ms()
    while True:
        if demo:
            phase = time.ticks_diff(time.ticks_ms(), t0) / 1500
            reading = 512 - 511 * math.cos(phase)
        else:
            reading = adc.read()
        average = average * 0.8 + reading * 0.2   # smoothing
        p = min(100, int(average * 100 / 1024 + 0.5))
        if p != current or first:
            first = False
            if p > current:
                paint_ring(current, p, True)
            else:
                paint_ring(p, current, False)
            current = p
            # covering the centre may have erased the texts: redraw them
            title_label("ADC")
            value_label("%d%%" % p)
            raw_label("raw %d" % int(average))
        time.sleep_ms(30)


main()
