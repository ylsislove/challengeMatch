import serial

class Base:
    def __init__(self):
        self.port = serial.Serial(port="/dev/serial0", baudrate=500000, writeTimeout=0)