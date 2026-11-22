#!/usr/bin/env bash
# Builds MicroPython for the ESP Round LCD (ESP8266 + GC9A01) with the C driver.
#
#   ./build.sh            build
#   ./build.sh clean      clean
#   ./build.sh deploy     flash (PORT=/dev/ttyUSB0 by default)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
MPY="$ROOT/micropython"
PORT_DIR="$MPY/ports/esp8266"
BOARD_DIR="$ROOT/boards/ESP_ROUND_LCD"
JOBS="${JOBS:-$(nproc)}"
export PATH="$ROOT/tools/xtensa-lx106-elf/bin:$PATH"

# --- Linker script: esp8266_2MiB.ld + esp8266_common.ld with the driver in irom0 ---
# Upstream only places in flash (irom0) the .o files it lists explicitly; everything
# else goes to IRAM (32 KiB), where the driver doesn't fit. Add the build/gc9a01/ objects.
mkdir -p "$BOARD_DIR/gen"
{
    sed '/^INCLUDE /d' "$PORT_DIR/boards/esp8266_2MiB.ld"
    sed 's|^\(\s*\)\*drivers/bus/\*\.o(.literal\* .text\*)|&\n\1*/gc9a01/*.o(.literal* .text*)|' \
        "$PORT_DIR/boards/esp8266_common.ld"
} > "$BOARD_DIR/gen/esp_round_lcd.ld"
grep -q '\*/gc9a01/\*\.o' "$BOARD_DIR/gen/esp_round_lcd.ld" \
    || { echo "ERROR: could not patch the linker script" >&2; exit 1; }

# --- Patches to MicroPython (patches/*.patch), idempotent ---
for p in "$ROOT"/patches/*.patch; do
    [ -e "$p" ] || continue
    if git -C "$MPY" apply --reverse --check "$p" 2>/dev/null; then
        :   # already applied
    elif git -C "$MPY" apply --check "$p" 2>/dev/null; then
        echo "Applying $(basename "$p")"
        git -C "$MPY" apply "$p"
    else
        echo "ERROR: patch $(basename "$p") does not apply" >&2; exit 1
    fi
done

# --- mpy-cross and submodules (first run only) ---
[ -x "$MPY/mpy-cross/build/mpy-cross" ] || make -C "$MPY/mpy-cross" -j"$JOBS"
[ -f "$MPY/lib/axtls/README" ] || make -C "$PORT_DIR" submodules

MAKE_ARGS=(BOARD_DIR="$BOARD_DIR" BUILD="$ROOT/build" -j"$JOBS")

case "${1:-}" in
    clean)  make -C "$PORT_DIR" "${MAKE_ARGS[@]}" clean ;;
    deploy) make -C "$PORT_DIR" "${MAKE_ARGS[@]}" PORT="${PORT:-/dev/ttyUSB0}" \
                 BAUD="${BAUD:-460800}" FLASH_MODE="${FLASH_MODE:-dio}" FLASH_SIZE=4MB deploy ;;
    *)      make -C "$PORT_DIR" "${MAKE_ARGS[@]}"
            ls -la "$ROOT/build/firmware.bin" ;;
esac
