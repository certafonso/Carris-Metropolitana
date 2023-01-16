""" 
Script to generate a combined timetable for a list of routes that have an endpoint in common
"""
from carris_metropolitana import get_all_route_trips

def generate_timetable(trips):
    """Generates a timetable where the first two columns are the stop id 
    and name and the remaining columns are the times at each stop.

    Args:
        trips (dict): A dictionary with all trips divided by line.

    Returns:
        list: A timetable
    """
    def get_stop_index(timetable, stop_id):
        for i in range(1,len(timetable)):
            if timetable[i][0] == stop_id:
                return i

        return -1

    def add_timetable_column(timetable, trip, header, no_time_string = "-"):
        """Adds a columns to the time table"""
        # Get number of columns already in timetable
        column_number = len(timetable[0]) - 2

        # Add header to first line
        timetable[0].append(header)

        last_stop_index = 0
        for stop in trip:
            stop_index = get_stop_index(timetable, stop["stop_id"])

            # Stop doesn't exist, add it after the last one
            if stop_index < 0:
                stop_index = last_stop_index + 1
                timetable.insert(stop_index, [stop["stop_id"], stop["stop_name"]] + [no_time_string] * column_number)

            # Add time to the line
            timetable[stop_index].append(stop["visual_time"])
            last_stop_index = stop_index

        # Ensure every column has the same lenght
        column_number = len(timetable[0])
        for line in timetable:
            if len(line) < column_number:
                line.append(no_time_string)

        return timetable
        
    timetable = [["", ""]]

    for route in trips:
        for trip in trips[route]:
            timetable = add_timetable_column(timetable, trip, route)

    return timetable

def sort_timetable_columns(timetable, sort_index):
    """Sorts the timetable columns using the hours in the sort_index line.

    Args:
        timetable (list): Timetable to sort
        sort_index (int | str): If set to an int defines the line we are using to sort.
            If it's set to a str it is the name of the station where we want to sort.

    Returns:
        list: Sorted timetable
    """
    def swap_timetable_columns(timetable, index1, index2):
        """Swaps 2 columns of a timetable"""
        for line in timetable:
            aux = line[index1]
            line[index1] = line[index2]
            line[index2] = aux

        return timetable

    time_to_int = lambda time: int(time.replace(":", ""))

    # A stop name was given, search for it's index
    if type(sort_index) == str:
        i = 1
        while timetable[i][1] != sort_index:
            i += 1

        sort_index = i

    # Sort timetable columns (first 2 columns are name and if so they are not sorted)
    for i in range(2, len(timetable[1])):
        for j in range(i+1, len(timetable[1])):
            if time_to_int(timetable[sort_index][i]) > time_to_int(timetable[sort_index][j]):
                timetable = swap_timetable_columns(timetable, i, j)

    return timetable

def generate_combined_timetable(base_url, route_list, first_stop_name, date):
    """Generates a timetable with all buses of routes on route_list. 
    The routes have to have a common last/first stop specified by first_stop_name.

    Args:
        base_url (str): Base url of the site, for example: https://horarios.carrismetropolitana.pt/
        route_list (list): List of route numbers
        first_stop_name (str): name of the first stop
        date (str): Date of the search

    Returns:
        list, list: timetables in each direction
    """
    trips = {str(route): get_all_route_trips(base_url, route, date) for route in route_list}
    
    # Separate trips in each direction
    oneway_trips = {}
    returning_trips  = {}
    for route in trips:
        oneway_trips[route] = []
        returning_trips[route] = []
        for trip in trips[route]:
            if trip[0]["stop_name"] == first_stop_name:
                oneway_trips[route].append(trip)
            else:
                returning_trips[route].append(trip)

    # Generate timetable in both directions
    oneway_timetable = generate_timetable(oneway_trips)
    returning_timetable = generate_timetable(returning_trips)

    return oneway_timetable, returning_timetable

def save_timetable_csv(timetable, filename):
    """Saves timetable as csv file.

    Args:
        timetable (list): timetable to save
        filename (str): filename of output
    """
    with open(filename, "w") as f:
        for line in timetable:
            f.write(",".join(line) + "\n")
