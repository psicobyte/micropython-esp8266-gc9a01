"""Configuracion de la placa "ESP Round LCD" (ESP-12S + GC9A01 240x240).

Pines (fijos en la placa):
    SCK  GPIO14  (HSPI, SPI(1))
    MOSI GPIO13  (HSPI, SPI(1))
    CS   GPIO15
    DC   GPIO2
    RST  GPIO16
    BL   GPIO12  (alto = encendida)

Uso:
    import round_lcd, gc9a01
    tft = round_lcd.display()
    tft.fill(gc9a01.BLUE)
"""

from machine import Pin, SPI
import gc9a01

WIDTH = 240
HEIGHT = 240

PIN_CS = 15
PIN_DC = 2
PIN_RST = 16
PIN_BL = 12

# Valores para scroll vertical (vscrdef), como en los tft_config del driver
TFA = 0
BFA = 0


def display(rotation=0, buffer_size=0, options=0, baudrate=80_000_000, cpu_freq=None):
    """Crea, inicializa y devuelve un objeto gc9a01.GC9A01 listo para usar.

    rotation: 0-7 (4-7 = espejado).
    buffer_size: 0 = buffer dinamico por operacion (recomendado en ESP8266,
        poca RAM). Un frame completo (240*240*2 = 115 KB) NO cabe.
    baudrate: SPI(1) hardware; 80 MHz (maximo del ESP8266) probado en esta placa.
    cpu_freq: None = no tocar; 160_000_000 casi duplica la velocidad de dibujo
        (fill: 28 ms -> 18 ms) a costa de algo mas de consumo.
    """
    if cpu_freq:
        import machine
        machine.freq(cpu_freq)
    spi = SPI(1, baudrate=baudrate, polarity=0, phase=0)
    tft = gc9a01.GC9A01(
        spi,
        WIDTH,
        HEIGHT,
        reset=Pin(PIN_RST, Pin.OUT),
        cs=Pin(PIN_CS, Pin.OUT),
        dc=Pin(PIN_DC, Pin.OUT),
        backlight=Pin(PIN_BL, Pin.OUT),
        rotation=rotation,
        options=options,
        buffer_size=buffer_size,
    )
    tft.init()
    return tft
