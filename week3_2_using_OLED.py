from machine import Pin, UART, I2C, Timer, ADC, PWM
from ssd1306 import SSD1306_I2C
from fifo import Fifo
import time


# Detect the turning direction of the rotary encoder
def rotary_handler(pin):
    global sensitivity
    sensitivity += 1
    
    if sensitivity == 2:
        sensitivity = 0
        
        if rotary_b.value():
            rotation_queue.put(1) # One step up
        else:
            rotation_queue.put(0)  # One step down


# Set a new selected row by toggling the rotary encoder. 
def toggle_handler(pin):
    global prev_press_time
    current_time = time.ticks_ms()
    
    # If the difference between last press and current is larger than min_interval --> There was no switch bounce detected
    if time.ticks_diff(current_time, prev_press_time) > min_interval:
        rotation_queue.put(2)
        prev_press_time = current_time


# Initialize the all leds
all_leds = [
    {"name": "LED1","led_status": " - OFF", "led_pin": PWM(Pin(22, Pin.OUT))},
    {"name": "LED2","led_status": " - OFF", "led_pin": PWM(Pin(21, Pin.OUT))},
    {"name": "LED3","led_status": " - OFF", "led_pin": PWM(Pin(20, Pin.OUT))}
    ]

# Initialize the OLED screen
i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled_width = 128
oled_height = 64
oled = SSD1306_I2C(oled_width, oled_height, i2c)

# Initialize the rotary encoder pins
rotary_a = Pin(10, Pin.IN, Pin.PULL_UP)
rotary_b = Pin(11, Pin.IN, Pin.PULL_UP)
rotary_sw = Pin(12, Pin.IN, Pin.PULL_UP)

# Time when last button press was done
prev_press_time = 0

# How many milliseconds should we wait to allow a new button push (Bounce filtering)
min_interval = 50

# Interrupt main program when the rotary encoder is turned - calls rotary_handler()
rotary_a.irq(trigger=Pin.IRQ_RISING, handler=rotary_handler)
rotary_sw.irq(trigger=Pin.IRQ_RISING, handler=toggle_handler)

# FIFO for queuing up rotations
rotation_queue = Fifo(20)

current_row = 0
sensitivity = 0
previous_action = ''
need_to_update_oled = True


while True:
    
    if need_to_update_oled:
        need_to_update_oled = False
        oled.fill(0)
        y = 0
    
        # For every LED make a line of text that has the name, status and cursor if selected
        for i, specific_led in enumerate(all_leds):
            
            name_text = specific_led['name']
            status_text = specific_led['led_status']   
            text_row = name_text + status_text
            
            if i == current_row:
                text_row += ' <--'
                
            oled.text(text_row, 15, y, 1)
            y += 15
        
        # After all the LEDs are in order, add text on what caused the update
        oled.text(previous_action, 0, y, 1)
        oled.show()
    
    # Check if there is queued up rotations in the FIFO
    if rotation_queue.has_data():
        
        rotation_direction = rotation_queue.get()
        need_to_update_oled = True
        
        # Number 2 is the self determmined status code for pushing down the rotary encoder
        if rotation_direction == 2:
            previous_action = 'Led toggled'
            
            selected_led = all_leds[current_row]
            led_status = selected_led['led_status']
            
            if led_status == " - OFF":
                selected_led['led_status'] = " - ON "
                selected_led['led_pin'].duty_u16(500)
                
            else:
                selected_led['led_status'] = " - OFF"
                selected_led['led_pin'].duty_u16(0)
        
        elif rotation_direction in [0, 1]:   
            previous_action = ' Encoder turned'
                
            # Check which way the rotary encoder was turned
            if rotation_direction == 1 and current_row < 2:
                current_row += 1
            elif rotation_direction == 0 and current_row > 0:
                current_row -= 1
                
