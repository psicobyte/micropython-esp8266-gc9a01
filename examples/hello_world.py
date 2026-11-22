# "Hello world" using the gc9a01 driver built into the firmware.
# Copy it to the board as main.py or run it with: mpremote run examples/hello_world.py
import gc9a01
import round_lcd
import vga1_bold_16x32 as big
import vga1_8x16 as small
import romans
import NotoSans_32 as noto

tft = round_lcd.display()
tft.fill(gc9a01.BLACK)

cx, cy = round_lcd.WIDTH // 2, round_lcd.HEIGHT // 2

# Coloured ring around the edge of the round display
tft.circle(cx, cy, 119, gc9a01.CYAN)
tft.circle(cx, cy, 117, gc9a01.MAGENTA)

# Bitmap text (ROM fonts)
msg = "Hello world"
tft.text(big, msg, cx - len(msg) * big.WIDTH // 2, cy - big.HEIGHT // 2,
         gc9a01.YELLOW, gc9a01.BLACK)

# Proportional font
w = tft.write_len(noto, "ESP8266")
tft.write(noto, "ESP8266", cx - w // 2, 50, gc9a01.GREEN, gc9a01.BLACK)

# Hershey vector font
w = tft.draw_len(romans, "GC9A01")
tft.draw(romans, "GC9A01", cx - w // 2, 170, gc9a01.WHITE)

tft.text(small, "240x240", cx - 7 * 4, 195, gc9a01.color565(255, 128, 0), gc9a01.BLACK)
