from machine import UART, Pin, I2C, ADC
from ssd1306 import SSD1306_I2C
from fifo import Fifo
from filefifo import Filefifo
import time


# Detect the turning direction of the rotary encoder
def rotary_handler(pin):
    global prev_rotation_time
    current_time = time.ticks_ms()
    
    # If the difference between last turn and current time is larger than min_interval --> There was no bounce detected
    if time.ticks_diff(current_time, prev_rotation_time) > min_interval:    
        prev_rotation_time = current_time
        if rotary_b.value():
            queued_rotations.put(1)  # One step up   
        else:
            queued_rotations.put(0)  # One step down
            
        
# Sort fifo class into a list of data and extract min/max values.
def sort_fifo(fifo_class, sample_count):
    all_data = []
    for _ in range(sample_count):
        sample = fifo_class.get()
        all_data.append(sample)

    highest_value = max(all_data)
    lowest_value = min(all_data)
        
    # Return data as a dictionary
    key_values = {
        'all_data' : all_data,
        'highest_value' : highest_value,
        'lowest_value' : lowest_value}
    return key_values


# Scale data to a desired range.
def scale_data(data_dictionary, bottom_limit, top_limit):
    highest_value = data_dictionary['highest_value']
    lowest_value = data_dictionary['lowest_value']
    all_data = data_dictionary['all_data']
    scaled_data = []
    
    for i in all_data:
        scaled_value = (((i - lowest_value) / (highest_value - lowest_value)) * (top_limit - bottom_limit)) + bottom_limit
        scaled_data.append(int(scaled_value))
    return scaled_data


# Update the values inside the scope depending on the rotation direction of the encoder by creating a new list
def move_scope(curr_cursor, scope_size, all_scaled_data):
    new_scope_first_index = curr_cursor
    new_scope_last_index = curr_cursor + scope_size
    current_scope = all_scaled_data[new_scope_first_index:new_scope_last_index]
    return current_scope 

    
# Show a list of already scaled values on the OLED screen
def display_on_oled(curr_scope, oled_class, line_color = 1):
    oled_class.fill(0)
    
    for i in range(len(curr_scope) - 1):
        x1 = i
        x2 = i + 1
        
         # Due to screen orientation we need to flip the y coordinate.
        y1 = oled_class.height - curr_scope[i]
        y2 = oled_class.height - curr_scope[i + 1]
        
        # Draw a line between (x1, y1) and (x2, y2)
        oled_class.line(x1, y1, x2, y2, line_color)
    oled_class.show()
    

# Initialize the rotary encoder pins
rotary_a = Pin(10, Pin.IN, Pin.PULL_UP)
rotary_b = Pin(11, Pin.IN, Pin.PULL_UP)

# How many milliseconds should we wait to allow a new rotation (Bounce filtering)
min_interval = 50
prev_rotation_time = 0

# Interrupt for the turning of the rotary encoder
rotary_a.irq(trigger=Pin.IRQ_RISING, handler=rotary_handler)

# FIFO for queuing up rotations
queued_rotations = Fifo(20)

# Initialize the OLED screen
i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled_width = 128
oled_height = 64
oled = SSD1306_I2C(oled_width, oled_height, i2c)

# Read data from a file using FileFifo
data = Filefifo(10, name = 'lib/capture_250Hz_01.txt')
sample_rate = 1000

# How many values should be in each window
scope_window = 128

# Save the data from the file
fifo_to_dict = sort_fifo(data, sample_rate)
scaled_data = scale_data(fifo_to_dict, 1, oled_height - 1)

# Scope is a list that has only the values shown to the user. Initialize the scope.
current_scope = scaled_data[:scope_window]
need_to_update_oled = True
cursor = 0

# Main loop
while True:
    if need_to_update_oled:
        scope_after_movement = move_scope(cursor, scope_window, scaled_data)
        current_scope = scope_after_movement
        display_on_oled(current_scope, oled)
        need_to_update_oled = False
        
    # Check if there is queued up rotations in the FIFO
    if queued_rotations.has_data():
        rotation_direction = queued_rotations.get()
        need_to_update_oled = True
        
        # Figure out the last index that fills the screen
        last_possible_index = len(scaled_data) - scope_window
        
         # Number 0 in the queue represents that the rotary encoder has been turned clockwise 
        if rotation_direction == 0:
            cursor += 12
            # Make sure that the cursor doesnt go above the uppermost limit
            if cursor > last_possible_index:
                cursor = last_possible_index
        
        # Number one in the queue represents that the rotary encoder has been turned counter clockwise
        elif rotation_direction == 1:
            cursor -= 12
            # Make sure that the cursor doesnt go negative
            if cursor < 0:
                cursor = 0
            