import time
from machine import UART, Pin, I2C, Timer, ADC
from ssd1306 import SSD1306_I2C

sw0 = Pin(9, Pin.IN, Pin.PULL_UP) # left
sw2 = Pin(7, Pin.IN, Pin.PULL_UP) # right

i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled_width = 128
oled_height = 64
oled = SSD1306_I2C(oled_width, oled_height, i2c)

class Ufo:
    def __init__(self,screen_width, right_button, left_button):
        self.max_width = screen_width - 24
        self.min_width = 0
        self.right_button = right_button
        self.left_button = left_button
        self.position = 0
        self.ufo_moving_left = 'false'
        self.ufo_moving_right = 'false'
        
    def show_ufo(self):
        oled.text('<=>', self.position, 0, 1)
        oled.show()
        oled.fill(0)
        
    def screen_edge_detection(self):
        if self.position == self.max_width:
            self.position = self.max_width
            self.ufo_moving_left = 'false'
            
        if self.position == self.min_width:
            self.position == self.min_width
            self.ufo_moving_right = 'false'
        
    def check_buttons(self):
        if self.right_button() == 0:
            self.ufo_moving_right = 'true'
            self.ufo_moving_left = 'false'
            
        if self.left_button() == 0:
            self.ufo_moving_left = 'true'
            self.ufo_moving_right = 'false'


    def run(self):
        while True:
            self.screen_edge_detection()
            self.show_ufo()
            
            if self.ufo_moving_left == 'true':
                self.position += 1
                
            elif self.ufo_moving_right == 'true':
                self.position -= 1
                
            self.check_buttons()
            
            
ufo = Ufo(128, sw2, sw0)
ufo.run()