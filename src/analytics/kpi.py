import pandas as pd

def calculate_speed(total_pieces, first_timestamp, last_timestamp):
    if first_timestamp is None or last_timestamp is None:
        return 0.0
    
    first_timestamp = pd.to_datetime(first_timestamp)
    last_timestamp = pd.to_datetime(last_timestamp)

    elapsed_seconds = (last_timestamp - first_timestamp).total_seconds()

    if elapsed_seconds<=0:
        return 0.0
    
    speed= (total_pieces / elapsed_seconds * 3600) 
    
    return speed


def calculate_cycle_speed(total_cycles, first_timestamp, last_timestamp):
    return calculate_speed(total_cycles, first_timestamp, last_timestamp)
    
def calculate_production_speed(total_production_pieces, first_timestamp, last_timestamp):
    return calculate_speed(total_production_pieces, first_timestamp, last_timestamp)
   