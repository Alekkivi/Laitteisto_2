import time
from machine import UART, Pin, I2C, Timer, ADC
from ssd1306 import SSD1306_I2C

i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled_width = 128
oled_height = 64
oled = SSD1306_I2C(oled_width, oled_height, i2c)


class Etch_a_sketch:
    def __init__(self, screen_object, up_button_pin, down_button_pin, reset_button_pin):
        self.oled = screen_object
        self.down_btn = Pin(up_button_pin, Pin.IN, Pin.PULL_UP)
        self.up_btn = Pin(down_button_pin, Pin.IN, Pin.PULL_UP)
        self.reset_btn = Pin(reset_button_pin, Pin.IN, Pin.PULL_UP)
        self.oled_width = screen_object.width
        self.oled_height = screen_object.height
        
        # Higher the value --> lower the position of the cursor
        self.cursor_height = self.oled_height // 2
        
        # Cursor is this many pixels from the left side of the screen
        self.cursor_width = 0

        
    # Clear sketch and reset cursor position    
    def reset_sketch(self):
        self.oled.fill(0)
        self.cursor_height = self.oled_height // 2
        self.cursor_width = 0
        
    # Check for button presses and make sure the cursor doesnt escape the limits of the screen
    def check_buttons(self):
        if self.down_btn() == 0 and self.cursor_height < self.oled_height - 1:
            self.cursor_height += 1
        
        elif self.up_btn() == 0 and self.cursor_height > 0:
            self.cursor_height -= 1
            
        elif self.reset_btn() == 0:
            self.reset_sketch()


    def run(self):
        while True:
            self.check_buttons()
            
            # Show current position of the cursor and continue on forwards
            oled.pixel(self.cursor_width, self.cursor_height, 1)
            oled.show()
            self.cursor_width += 1
            
            # Bring cursor back to the left when right edge reached
            if self.cursor_width >= self.oled_width:
                self.cursor_width = 0

# Main programme
Etch1 = Etch_a_sketch(oled, 9, 7, 8)
Etch1.run()
