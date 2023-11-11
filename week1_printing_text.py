import time
from machine import UART, Pin, I2C, Timer, ADC
from ssd1306 import SSD1306_I2C

i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled_width = 128
oled_height = 64
oled = SSD1306_I2C(oled_width, oled_height, i2c)


class Printer:
    def __init__(self, screen_object):
        self.oled = screen_object
        self.shown_strings = []
        
    # Maintain a list of 8 inputs, oldest item will be over written.     
    def get_user_input(self):
        user_input = input('input a string: ')  
        if len(self.shown_strings) < 8:
            self.shown_strings.append(user_input)
        else:
            self.shown_strings.pop(0)
            self.shown_strings.append(user_input)
            
    
    def show_user_input(self):
        self.oled.fill(0)
        self.get_user_input()
        
        y = 0
        for text_line in self.shown_strings:
            self.oled.text(text_line, 0, y, 1)
            y += 8
            
        self.oled.show()   
            
    def run(self):
        while True:
            self.show_user_input()

# Main programme
printer = Printer(oled)
printer.run()

        