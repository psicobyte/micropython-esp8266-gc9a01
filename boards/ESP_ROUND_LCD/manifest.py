# Same as ESP8266_GENERIC/manifest_2MiB.py + the round display modules.

include("$(PORT_DIR)/boards/manifest.py")
include("$(MPY_DIR)/extmod/asyncio")

require("ssd1306")
require("upysh")
require("umqtt.simple")
require("umqtt.robust")

# --- GC9A01 display ---
# Helper with the board's pinout: round_lcd.py
freeze("$(BOARD_DIR)/../../modules")

# Driver fonts (gc9a01_mpy/modules). Only a few are frozen to save flash;
# the rest can be copied to the filesystem.
_FONTS = "$(BOARD_DIR)/../../gc9a01_mpy/modules"
for _f in (
    "vga1_8x8.py",          # bitmap 8x8   -> tft.text()
    "vga1_8x16.py",         # bitmap 8x16  -> tft.text()
    "vga1_bold_16x32.py",   # bitmap 16x32 -> tft.text()
    "romans.py",            # Hershey vector -> tft.draw()
    "NotoSans_32.py",       # proportional -> tft.write()
):
    freeze(_FONTS, _f)
