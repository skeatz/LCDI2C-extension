from machine import Pin, I2C
import os

machine = os.uname().machine
if ("KidBright32" in machine) or ("KidMotor V4" in machine):
    i2c1 = I2C(1, scl=Pin(5), sda=Pin(4), freq=400000)
elif "Mbits" in machine:
    i2c1 = I2C(0, scl=Pin(21), sda=Pin(22), freq=400000)
else:
    i2c1 = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)


LCDI2C_ADDR = 0x3F

PIN_RS = False

BIT_EN = 0x04
BIT_RS = 0x01
BIT_BLACKLIGHT = 0x08

BIT_BLINK = 0x01
BIT_CURSOR = 0x02
BIT_DISPLAY = 0x04

BLINK = False
CURSOR = False
sDISPLAY = True
BLACKLIGHT = True

def writeD(data):
    data = bytes([ data ])
    i2c1.writeto(LCDI2C_ADDR, data)

def SEND(data):
    data = (BIT_BLACKLIGHT if BLACKLIGHT else 0) | (BIT_RS if PIN_RS else 0) | data
    writeD(data)
    writeD(BIT_EN | data)
    writeD(data)

def CMD(data=0):
    global PIN_RS
    PIN_RS = False
    SEND(data&0xF0)
    SEND((data<<4)&0xF0)
    PIN_RS = True

def backlight(on=None):
    global BLACKLIGHT
    if on != None:
        BLACKLIGHT = on
        CMD(0)
    return BLACKLIGHT

def clear():
    CMD(0x01)

def dispUpdate():
    CMD(0x08 | (BIT_BLINK if BLINK else 0) | (BIT_CURSOR if CURSOR else 0) | (BIT_DISPLAY if sDISPLAY else 0))

def blink(v=None):
    global BLINK
    if v != None:
        BLINK = v
        dispUpdate()
    return BLINK

def cursor(v=None):
    global CURSOR
    if v != None:
        CURSOR = v
        dispUpdate()
    return CURSOR

def display(v=None):
    global sDISPLAY
    if v != None:
        sDISPLAY = v
        dispUpdate()
    return sDISPLAY

def setup(addr=0x3F, col=20, row=4):
    global LCDI2C_ADDR
    LCDI2C_ADDR = addr
    for a in ( 0x30, 0x30, 0x30, 0x20 ):
        SEND(a)
    CMD(0x20 | 0x08 if row > 1 else 0)
    dispUpdate()
    clear()

def setupAuto():
    scan_addr = i2c1.scan()
    addr = None
    if 0x27 in scan_addr:
        addr = 0x27
    if 0x3F in scan_addr:
        addr = 0x3F
    if addr:
        setup(addr)

def setCursor(line=1, indent=0):
    CMD(( 0x80, 0xC0, 0x94, 0xD4 )[line - 1] + indent)

def show(data, line=None, indent=0):
    global PIN_RS
    if line != None:
        setCursor(line, indent)
    PIN_RS = True
    for d in bytearray(str(data)):
        SEND(d&0xF0)
        SEND((d<<4)&0xF0)

def scrollLeft():
    CMD(0x18)

def scrollRight():
    CMD(0x1C)
