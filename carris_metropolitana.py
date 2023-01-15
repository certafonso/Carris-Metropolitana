import requests
from time import sleep

def do_request(base_url, action, delay = 0.1, **args):
    """Executes a resquest to the server

    Args:
        base_url (str): Base url of the site, for example: https://horarios.carrismetropolitana.pt/
        action (str): Action to be executed
        delay (int, optional): Delay to avoid doing to many request to the server

    Returns:
        dict: Json response of the request.
    """
    url = [base_url + f"?action={action}"]
    url += [f"{arg}={args[arg]}" for arg in args]
    url = "&".join(url)

    print(f"Executing {url} in {delay} seconds.")
    sleep(delay)

    return requests.get(url).json()

def get_timetable(base_url, route_number, way, date, variant = 0) -> dict:
    """Get the raw timetables of a route

    Args:
        base_url (str): Base url of the site, for example: https://horarios.carrismetropolitana.pt/
        route_number (str | int): Number of the route.
        way (str | int): Direction of the route, starts with one and is the same order as in the oficial site
        date (str): Date of the search
        variant (int, optional): Variant of the line, starts with zero and is in the same order as in the oficial site. Defaults to 0.

    Returns:
        dict: Json repsentation of the time table with the following format:
        {stop_id: {hour:minutes, ...},...}
    """
    return do_request(
        base_url,
        "cmet_get_route_timetable",
        route_id=f"{route_number}_{variant}",
        way_id=f"{route_number}_{variant}_{way}",
        start_date=date,
        )

def get_stop_name(base_url, stop_id, name_dict = {}):
    """Get the name of a stop with a given id. This function is broken because the API was changed and I dind't find the new action name (yet).

    Args:
        base_url (str): Base url of the site, for example: https://horarios.carrismetropolitana.pt/
        stop_id (str): Id of the stop.
        name_dict (dict, optional): Dictionary to cache names of stations to reduce number of requests. Defaults to {}.

    Returns:
        _type_: _description_
    """
    raise NotImplementedError("This function is broken because the API was changed and I dind't find the new action name (yet)")
    
    try:
        return name_dict[stop_id]
    except KeyError:
        name = do_request(
            base_url,
            "carris_get_stop_name_by_id",
            stop_id=stop_id
        )
        name_dict[stop_id] = name
        return name

def get_timetable_with_names(base_url, route_number, way, date, variant = 0, name_dict = {}):
    """Get the timetables of a route with the names of the stops. This function is broken because get_stop_name is broken.

    Args:
        base_url (str): Base url of the site, for example: https://horarios.carrismetropolitana.pt/
        route_number (str | int): Number of the route.
        way (str | int): Direction of the route, starts with one and is the same order as in the oficial site
        date (str): Date of the search
        variant (int, optional): Variant of the line, starts with zero and is in the same order as in the oficial site. Defaults to 0.
        name_dict (dict, optional): Dictionary to cache names of stations to reduce number of requests. Defaults to {}.

    Returns:
        dict: Json repsentation of the time table with the following format:
        {stop_name: {hour:minutes, ...},...}
    """
    raw_times = get_timetable(base_url, route_number, way, date, variant)

    times = {}
    for stop in raw_times:
        stop_name = get_stop_name(base_url, stop, name_dict)
        times[stop_name] = raw_times[stop]

    return times

def get_route_stops(base_url, route_number, way, date, variant = 0):
    """Get the stops with time of a specified route.

    Args:
        base_url (str): Base url of the site, for example: https://horarios.carrismetropolitana.pt/
        route_number (str | int): Number of the route.
        way (str | int): Direction of the route, starts with one and is the same order as in the oficial site
        date (str): Date of the search
        variant (int, optional): Variant of the line, starts with zero and is in the same order as in the oficial site. Defaults to 0.

    Returns:
        dict: a dictionary with 2 keys: "stops" and "hours". The first one contains a list of dicts all representing a time a bus stops
        with the keys: trip_id, arrival_time, visual_time, departure_time, stop_id, stop_sequence, stop_name, stop_lat and stop_lon.
        The second one contains pretty much the same info but with just trip_id, stop_id, stop_sequence, arrival_time and visual_time.
    """
    return do_request(
        base_url,
        "cmet_get_route_stops",
        route_id=f"{route_number}_{variant}",
        way_id=f"{route_number}_{variant}_{way}",
        start_date=date,
        )

def get_route_trips(base_url, route_number, way, date, variant = 0):
    """Get trips for a specified route.

    Args:
        base_url (str): Base url of the site, for example: https://horarios.carrismetropolitana.pt/
        route_number (str | int): Number of the route.
        way (str | int): Direction of the route, starts with one and is the same order as in the oficial site
        date (str): Date of the search
        variant (int, optional): Variant of the line, starts with zero and is in the same order as in the oficial site. Defaults to 0.

    Returns:
        list: A list with the route trips with the format [trip1, trip2, ...]
        where trips are lists of the stops with format:
        {"stop_id": ..., "stop_sequence": ..., "visual_time": ..., "route": ..., "stop_name": ..., ...}
    """
    route_stops = get_route_stops(base_url, route_number, way, date, variant)
    
    trips = {}

    # Group stops by trips
    for stop in route_stops["stops"]:
        try:
            trips[stop["trip_id"]].append(stop)

        except KeyError:
            trips[stop["trip_id"]] = [stop]

    return [trips[trip_id] for trip_id in trips]

def get_all_route_trips(base_url, route_number, date):
    """Get all trips for specified route (all variants and ways).

    Args:
        base_url (str): Base url of the site, for example: https://horarios.carrismetropolitana.pt/
        route_number (str | int): Number of the route.
        date (str): Date of the search

    Returns:
        list: A list with the route trips with the format [trip1, trip2, ...]
        where trips are lists of the stops with format {"stop_id": ..., "stop_sequence": ..., "visual_time": ...}
    """
    all_trips = []
    
    for way in [1,2]:
        variant = 0
        while True:
            trips = get_route_trips(base_url, route_number, way, date, variant)

            if len(trips) == 0:
                break

            all_trips += trips

            variant += 1

    return all_trips
