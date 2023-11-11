from filefifo import Filefifo

# Sort fifo class into a list of data and extract min/max values for x ammout of seconds.
def sort_fifo(fifo_class, seconds_of_data, sample_frequency):
    
    # How many samples are needed to fill the wanted timeframe
    sample_count = seconds_of_data * sample_frequency
    
    all_data = []
    for i in range(sample_count):
        
        # To get a grasp of what the sample value is, you can just print(sample).
        sample = fifo_class.get()
        all_data.append(sample)
        
        # Establish base values on first iteration
        if i == 0:
            highest_value = sample
            lowest_value = sample
        
        # Compare next value to previous iterations to determine min and max
        elif sample > highest_value:
            highest_value = sample
            
        elif sample <= lowest_value:
            lowest_value = sample
    
    # Return data as a dictionary
    key_values = {
        'all_data' : all_data,
        'highest_value' : highest_value,
        'lowest_value' : lowest_value,
        'dataset_frequency' : sample_frequency,
        'amount_of_samples' : sample_count,
        'dataset_duration' : seconds_of_data
        }
    return key_values


# Scale data to the range of 0 - 100.
def scale_data(data_dictionary):
    highest_value = data_dictionary['highest_value']
    lowest_value = data_dictionary['lowest_value']
    all_data = data_dictionary['all_data']
    scaled_data = []
    
    for i in all_data:
        scaled_value = ((i - lowest_value) / (highest_value - lowest_value)) * 100
        scaled_data.append(scaled_value)
        
    # Add a new key-value pair to the existing data_dictionary    
    data_dictionary['scaled_data'] = scaled_data
    
    return data_dictionary

# Main program starts
data = Filefifo(10, name = 'lib/capture_250Hz_01.txt')
sample_frequency = 250

data_for_ten_seconds = sort_fifo(data, 10, sample_frequency)
scaled_ten_seconds = scale_data(data_for_ten_seconds)

for scaled_value in scaled_ten_seconds['scaled_data']:
    print(scaled_value)
    