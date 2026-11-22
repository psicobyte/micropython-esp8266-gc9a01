# Analog clock for the round display.
#
# Shows: rotated fill_polygon(), fill_circle(), line(), text() and write().
# Hands are erased by redrawing them in black (no full-screen flicker).
#
# Time: if the board is connected to WiFi it syncs over NTP (UTC + UTC_OFFSET);
# otherwise it uses the internal RTC as is. To set it from your PC:
#   mpremote rtc --set + run examples/clock.py
import math
import time

import gc9a01
import round_lcd
import vga1_8x16 as small
import NotoSans_32 as noto

UTC_OFFSET = 1  # NTP only: hours from UTC (e.g. Central European Time: 1 in winter, 2 in summer)

DAY_NAMES = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")

GREY = gc9a01.color565(90, 90, 90)
ORANGE = gc9a01.color565(255, 140, 0)
BACKGROUND = gc9a01.BLACK

tft = round_lcd.display(cpu_freq=160_000_000)
CX, CY = round_lcd.WIDTH // 2, round_lcd.HEIGHT // 2


def sync_ntp():
    try:
        import network
        import ntptime

        if network.WLAN(network.STA_IF).isconnected():
            ntptime.settime()  # sets the RTC to UTC
            return True
    except Exception as e:
        print("NTP failed:", e)
    return False


def hand_polygon(length, width, tail):
    """Convex polygon for a hand pointing up (12 o'clock)."""
    return [
        (0, tail),
        (-width, tail - width),
        (-width, -int(length * 0.7)),
        (0, -length),
        (width, -int(length * 0.7)),
        (width, tail - width),
        (0, tail),
    ]


HOUR_HAND = hand_polygon(52, 5, 12)
MINUTE_HAND = hand_polygon(80, 4, 14)
SECOND_HAND = [(-1, 20), (-1, -82), (1, -82), (1, 20), (-1, 20)]  # < 84: doesn't touch the numerals


def draw_dial():
    tft.fill(BACKGROUND)
    tft.circle(CX, CY, 119, GREY)
    for i in range(60):
        a = i * math.pi / 30
        s, c = math.sin(a), math.cos(a)
        r0 = 104 if i % 5 == 0 else 112
        color = gc9a01.WHITE if i % 5 == 0 else GREY
        tft.line(int(CX + r0 * s), int(CY - r0 * c),
                 int(CX + 116 * s), int(CY - 116 * c), color)
    for n, (dx, dy) in ((12, (0, -92)), (3, (92, 0)), (6, (0, 92)), (9, (-92, 0))):
        txt = str(n)
        tft.text(small, txt, CX + dx - len(txt) * 4, CY + dy - 8,
                 gc9a01.WHITE, BACKGROUND)


def draw_date(t):
    date = "%s %02d/%02d" % (DAY_NAMES[t[6]], t[2], t[1])
    hhmm = "%02d:%02d" % (t[3], t[4])
    tft.text(small, date, CX - len(date) * 4, CY + 34, ORANGE, BACKGROUND)
    w = tft.write_len(noto, hhmm)
    tft.write(noto, hhmm, CX - w // 2, CY - 70, GREY, BACKGROUND)


def hand_angles(t):
    # The minute hand moves 1 degree every 10 s and the hour hand once a minute,
    # so they are only erased/redrawn when their position actually changes.
    h, m, s = t[3] % 12, t[4], t[5]
    return (
        (h + m / 60) * math.pi / 6,
        (m + (s // 10) / 6) * math.pi / 30,
        s * math.pi / 30,
    )


def main():
    if sync_ntp():
        print("Time synced over NTP")
        offset = UTC_OFFSET * 3600
    else:
        print("No WiFi: using the internal RTC")
        offset = 0

    draw_dial()
    prev = None  # angles last drawn (hour, minute, second)
    last_second = -1
    while True:
        t = time.localtime(time.time() + offset)
        if t[5] == last_second:
            time.sleep_ms(20)
            continue
        last_second = t[5]
        hour_a, minute_a, second_a = hand_angles(t)

        # erase the previous hands by painting them in the background colour
        # (each hand is erased whenever its angle has changed, for any reason)
        if prev:
            prev_hour_a, prev_minute_a, prev_second_a = prev
            tft.fill_polygon(SECOND_HAND, CX, CY, BACKGROUND, prev_second_a)
            if prev_minute_a != minute_a:
                tft.fill_polygon(MINUTE_HAND, CX, CY, BACKGROUND, prev_minute_a)
            if prev_hour_a != hour_a:
                tft.fill_polygon(HOUR_HAND, CX, CY, BACKGROUND, prev_hour_a)
        # the texts may have been covered/erased by the hands
        draw_date(t)

        tft.fill_polygon(HOUR_HAND, CX, CY, gc9a01.WHITE, hour_a)
        tft.fill_polygon(MINUTE_HAND, CX, CY, gc9a01.WHITE, minute_a)
        tft.fill_polygon(SECOND_HAND, CX, CY, gc9a01.RED, second_a)
        tft.fill_circle(CX, CY, 5, gc9a01.RED)
        tft.fill_circle(CX, CY, 2, BACKGROUND)
        prev = (hour_a, minute_a, second_a)


main()
