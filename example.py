"""
Example: download timetables for buses for Campo Grande that pass trough Mafra
"""

from timetables import generate_combined_timetable, sort_timetable_columns, save_timetable_csv, filter_timetable

base_url = "https://horarios.carrismetropolitana.pt/"
first_stop_name = "Campo Grande"

# Download all timetables and divide them by direction
oneway_timetable, returning_timetable = generate_combined_timetable(
    base_url, 
    [
        2802, 
        2803, 
        2804, 
        2740, 
        2741, 
        2801, 
        2751, 
        2742, 
        2758, 
        2805, 
        2807
        ],
    first_stop_name, 
    "2023-01-28"
    )

# Stort timetables by time at Campo Grande
oneway_timetable = sort_timetable_columns(oneway_timetable, first_stop_name)
returning_timetable = sort_timetable_columns(returning_timetable, first_stop_name)

# Save timetables as csv
save_timetable_csv(oneway_timetable, f"./times from {first_stop_name}.csv")
save_timetable_csv(returning_timetable, f"./times to {first_stop_name}.csv")

# Filter only stops in Ericeira, Mafra, Venda do Pinheiro and Campo Grande
stops_filter = [
    "Ericeira (Terminal Rodoviário)", 
    "R Santa Casa Misericórdia 10 (Terminal)", 
    "Venda Do Pinheiro (Eco Parque)", 
    "Campo Grande"
    ]

filtered_oneway_timetable = filter_timetable(oneway_timetable, stops_filter)
filtered_returning_timetable = filter_timetable(returning_timetable, stops_filter)

save_timetable_csv(filtered_oneway_timetable, f"./times from {first_stop_name} filtered.csv")
save_timetable_csv(filtered_returning_timetable, f"./times to {first_stop_name} filtered.csv")
