import requests
from time import sleep

def do_request(base_url, action, delay = 1, **args):
    """Executes a resquest to the server

    Args:
        base_url (str): Base url of the site, for example: https://area2.carrismetropolitana.pt
        action (str): Action to be executed
        delay (int, optional): Delay to avoid doing to many request to the server

    Returns:
        dict: Json response of the request.
    """
    url = [base_url + f"/wp-admin/admin-ajax.php?action={action}"]
    url += [f"{arg}={args[arg]}" for arg in args]
    url = "&".join(url)

    print(f"Executing {url} in {delay} seconds.")
    sleep(delay)

    return requests.get(url).json()

def get_timetable(base_url, route_number, way, date, variant = 0) -> dict:
    """Get the raw timetables of a route

    Args:
        base_url (str): Base url of the site, for example: https://area2.carrismetropolitana.pt
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
        "carris_get_route_timetable",
        route_id=f"{route_number}_{variant}",
        way_id=f"{route_number}_{variant}_{way}",
        start_date=date,
        )

def get_stop_name(base_url, stop_id, name_dict = {}):
    """Get the name of a stop with a given id

    Args:
        base_url (str): Base url of the site, for example: https://area2.carrismetropolitana.pt
        stop_id (str): Id of the stop.
        name_dict (dict, optional): Dictionary to cache names of stations to reduce number of requests. Defaults to {}.

    Returns:
        _type_: _description_
    """
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
    """Get the timetables of a route with the names of the stops.

    Args:
        base_url (str): Base url of the site, for example: https://area2.carrismetropolitana.pt
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
        print(stop, stop_name)
        times[stop_name] = raw_times[stop]

    return times

def get_route_trips(base_url, route_number, way, date, variant = 0):
    timetable = get_timetable(base_url, route_number, way, date, variant)
    
    trips = []

    for stop_sequence, stop in enumerate(timetable):
        trip_count = 0
        for hour in timetable[stop]:
            for minute in timetable[stop][hour]:
                print(trips)
                try:
                    trips[trip_count].append({
                        "stop_id": stop,
                        "stop_sequence": stop_sequence,
                        "visual_time": f"{hour}:{minute}"
                    })
                except IndexError:
                    trips.append([{
                        "stop_id": stop,
                        "stop_sequence": stop_sequence,
                        "visual_time": f"{hour}:{minute}"
                    }])

                trip_count += 1

    return trips

def get_combined_timetables(base_url, route_list, way_list, date):

    combined_times = []
    for i in range(len(route_list)):
        timetable = get_timetable(
            base_url,
            route_list[i],
            way_list[i],
            date
        )
        print(timetable)
        for stop in timetable:
            try: combined_times[stop]
            except KeyError: combined_times[stop] = []
            for hour in timetable[stop]:
                for minute in timetable[stop][hour]:
                        combined_times[stop].append({
                            "route": route_list[i],
                            "hour": hour,
                            "minute": minute
                        })

    return combined_times

if __name__ == "__main__":
    import json
    base_url = "https://area2.carrismetropolitana.pt"

    # print(get_timetable(
    #     base_url,
    #     2804,
    #     1,
    #     "2023-01-03",
    #     0,
    # ))

    with open("trips.json", "w") as f:
        json.dump(
            get_route_trips(
                base_url,
                2801,
                1,
                "2023-01-03",
                0,
            ),
            f
        )

    # print(get_combined_timetables(
    #     base_url,
    #     [2804, 2740],
    #     [1,2],
    #     "2023-01-03",
    # ))