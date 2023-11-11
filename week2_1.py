from filefifo import Filefifo

# Sort fifo class into a list of data and extract min/max values.
def sort_fifo(fifo_class, sample_count, sample_frequency):
    
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
        'amount_of_samples' : len(all_data),
        'dataset_duration' : len(all_data) / sample_frequency
        }
    return key_values
    

# Find and calculate the number of peaks, time between them and the frequency of the signal. 
def peak_detection(data_dictionary):
    
    # Sort out some values from the dictionary for readability:
    dataset_duration = data_dictionary['dataset_duration']
    sample_count = data_dictionary['amount_of_samples']
    list_of_values = data_dictionary['all_data']
    highest_value = data_dictionary['highest_value']
    dataset_frequency = data_dictionary['dataset_frequency']
    found_peaks = []
    
    # Iterate over every sample in the datasest and compare it to the following one.
    for i, sample in enumerate(list_of_values):
        
        # If current sample has the highest value in the dataset and the next one is lower --> slope is decreasing and peak has been detected
        if sample == highest_value and list_of_values[i + 1] < highest_value:
            found_peaks.append(i)
            
    # After iterating over every datapoint, calculate how many peaks were found in total
    number_of_peaks = len(found_peaks)
    
    # Calculate the frequency of the signal
    peak_frequency = number_of_peaks / dataset_duration
    signal_frequency = 1 / peak_frequency
    
    # Iterate over the found_peaks list. This loop is only for printing out the location and time between the peaks.
    for i in range(number_of_peaks - 1):
        peak = found_peaks[i]
        following_peak = found_peaks[i + 1]
        time_between_subsequent_peaks =  (following_peak - peak) / dataset_frequency
        print('Time between peak x = ' + str(peak) + ' and peak x = ' + str(following_peak) + ' is: ' + str(time_between_subsequent_peaks) + 's')
        
    print('\nThere was total of {} peaks found'.format(number_of_peaks))
    print('The frequency of the signal was {:.2f}Hz'.format(signal_frequency))


# Main program starts
data = Filefifo(10, name = 'lib/capture_250Hz_01.txt')
sample_rate = 2572
sample_frequency = 250

data_dictionary = sort_fifo(data, sample_rate, sample_frequency)
peak_detection(data_dictionary)
