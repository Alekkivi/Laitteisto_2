from machine import Pin,PWM
from fifo import Fifo
import time


# Detect the turning direction of the rotary encoder
def rotary_handler(pin):
    if rotary_b.value():
        rotation_queue.put(1)  # One step up
    else:
        rotation_queue.put(0)  # One step down

# Set a new selected row by toggling the rotary encoder. 
def toggle_handler(pin):
    global prev_press_time
    current_time = time.ticks_ms()
    
    # If the difference between last press and current is larger than min_interval --> There was no switch bounce detected
    if time.ticks_diff(current_time, prev_press_time) > min_interval:
        
        rotation_queue.put(9)
        prev_press_time = current_time


# Initialize the LED pins
LED1 = PWM(Pin(22, Pin.OUT))
LED2 = PWM(Pin(21, Pin.OUT))
LED3 = PWM(Pin(20, Pin.OUT))

leds_info = [
    {"name": "LED1","led_status": " - OFF", "led_pin": LED1},
    {"name": "LED2","led_status": " - OFF", "led_pin": LED2},
    {"name": "LED3","led_status": " - OFF", "led_pin": LED3}
    ]

# Initialize the rotary encoder pins
rotary_a = Pin(10, Pin.IN, Pin.PULL_UP)
rotary_b = Pin(11, Pin.IN, Pin.PULL_UP)
rotary_sw = Pin(12, Pin.IN, Pin.PULL_UP)

# Time when last button press was done
prev_press_time = 0

# How many milliseconds should we wait to allow a new button push (Bounce filtering)
min_interval = 50

# Interrupt for the turning or toggling the rotary encoder
rotary_a.irq(trigger=Pin.IRQ_RISING, handler=rotary_handler)
rotary_sw.irq(trigger=Pin.IRQ_RISING, handler=toggle_handler)

# FIFO for queuing up rotations
rotation_queue = Fifo(20)

current_row = 0
need_to_update_menu = False
previous_action = ''


# Iterate over the led dictionaries to print out a menu to the console
def print_menu(leds_info, curr_row, previous_status):
    global need_to_update_menu
    
    for i, dictionary in enumerate(leds_info):
        
        led_name = dictionary['name']
        led_status = dictionary['led_status']
        text_row = led_name + led_status
        
        if i == current_row:
            text_row = "[ " + text_row + " ]"
            
        print(text_row)
    print(previous_action)
    print('\n')
    need_to_update_menu = False
        
        
#Main program
while True:
    time.sleep_ms(10)
    
    # If there has been changes made, print a up-to-date menu
    if need_to_update_menu: 
        print_menu(leds_info, current_row, previous_action)

    # If there is queued up rotations, iterate over them
    while rotation_queue.has_data():
        
        rotation_direction = rotation_queue.get()
        need_to_update_menu = True
        
        # 9 is just a number to represent that there's a queued up toggle in the FIFO
        if rotation_direction == 9:
            
            # What dictionary has the same index as the current row variable
            current_led = leds_info[current_row]
            
            # Because the button was pushed, we want to toggle the led ON or OFF depending on its previous state
            if current_led['led_status'] == " - OFF":
                current_led['led_status'] = " - ON"
                current_led['led_pin'].duty_u16(400)
            
            else:
                current_led['led_status'] = " - OFF"
                current_led['led_pin'].duty_u16(0)
            previous_action = '< Led toggled >'
        
        # Depending on the queued up variables in the FIFO, change the current row according to the rotation direction        
        if rotation_direction == 1 and current_row < 2:
            current_row += 1
            previous_action = '< Encoder turned >'
            
        elif rotation_direction == 0 and current_row > 0:
            current_row -= 1
            previous_action = '< Encoder turned >'
    
