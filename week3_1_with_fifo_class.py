from machine import Pin, PWM
from fifo import Fifo
import time

# Queues up rotation directions to the FIFO depending on the movement of the rotary encoder
def rotary_handler(pin):
    
    # This function is only reached when rotary_a sends an rising signal, so A == 1 here.
    if rotary_b.value():
        queued_rotations.put(1) # Counter clockwise
    else:
        queued_rotations.put(0) # Clockwise
        
        
# Toggle brightness percentage to 0 or 100 depending if the button is pressed
def check_led_toggle(button_pin, current_brightness_percentage):
    
    if not button_pin.value():
        while not button_pin.value():
            time.sleep(0.1)
        else:
            # This part is only reached when button has been pressed and let go
            if current_brightness_percentage > 0:
                current_brightness_percentage = 0
            else:
                current_brightness_percentage = 100
    return current_brightness_percentage
               
               
# Scale percentage to match equivelant LED brightness value
def percentage_to_led_value(current_brightness, led_max_brightness):
    scaled_value = int((current_brightness / 100) * led_max_brightness)
    return scaled_value

        
# Establish the rotary encoder
rotary_a = Pin(10, Pin.IN, Pin.PULL_UP)
rotary_b = Pin(11, Pin.IN, Pin.PULL_UP)
rotary_sw = Pin(12, Pin.IN, Pin.PULL_UP)

# Establish the LED
led = PWM(Pin(22, Pin.OUT))
led_max_brightness = 2000
led.freq(1000)

# Percentage to scale the LEDs value
current_brightness_percentage = 100

# FIFO - Store the queued up rotations  
queued_rotations = Fifo(20)

# Interrupt main program when the rotary encoder is turned - calls rotary_handler()
rotary_a.irq(trigger=Pin.IRQ_RISING, handler=rotary_handler)


# Main program
while True:
    time.sleep_ms(50)
    
    # Check if encoder switch has been pushed to toggle the LED
    brightness_after_toggle = check_led_toggle(rotary_sw, current_brightness_percentage)
    current_brightness_percentage = brightness_after_toggle
    
    # convert percentage to LED value on the scale of: 0 - max value
    scaled_brightness = percentage_to_led_value(current_brightness_percentage, led_max_brightness)
    
    # This controlls the LED
    led.duty_u16(scaled_brightness)
    
    # Brightness can only be altered when there's queued up directions and when the LED is on
    while queued_rotations.has_data() and current_brightness_percentage > 0:
        rotation_direction = queued_rotations.get()
        
        if rotation_direction == 1 and current_brightness_percentage > 2:
            print('counter clockwise')
            current_brightness_percentage -= 2
            
        elif rotation_direction == 0 and current_brightness_percentage < 98:
            print('clockwise')
            current_brightness_percentage += 2

