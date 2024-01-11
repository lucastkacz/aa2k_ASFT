from pdf_processing.ASFT_Data import ASFT_Data
import pandas as pd
from pathlib import Path
from typing import Optional, Union
from excel_generation.functions.excel_operations import append_dataframe_to_excel


def measurements_table(data: ASFT_Data) -> pd.DataFrame:
    measurements = data.measurements_with_chainage
    measurements_df = pd.DataFrame(
        {
            "key_1": data.key_1,
            "progresiva": measurements["Chainage"],
            "distancia": measurements["Distance"],
            "fricción": measurements["Friction"],
            "velocidad": measurements["Speed"],
            "prom. fricción 100m": measurements["Av. Friction 100m"],
            "criticidad": measurements["Color Code"],
        }
    )

    return measurements_df


def information_table(data: ASFT_Data) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "id_1": [data.id_1],
            "id_2": [data.id_2],
            "fecha": [data.friction_measurement_report.loc[0, "Date and Time"]],
            "iata": [data.configuration.loc[0, "iata"]],
            # "numbering": [data.numbering],
            # "side": [data.side],
            # "separation": [data.separation],
            # "runway": [data.runway],
            # "average speed": [data.average_speed],
            # "fric_A": [data.fric_A],
            # "fric_B": [data.fric_B],
            # "fric_C": [data.fric_C],
            # "runway length": [data.runway_length],
            # "starting point": [data.starting_point],
            # "equipment": [data.equipment],
            # "pilot": [data.pilot],
            # "ice level": [data.ice_level],
            # "tyre pressure": [data.tyre_pressure],
            # "water film": [data.water_film],
            # "system distance": [data.system_distance],
            # "operator": [data.operator],
            # "temperature": [data.temperature],
            # "surface condition": [data.surface_condition],
            # "weather": [data.weather],
            # "runway material": [data.runway_material],
        }
    )


def add_data_to_db(data: ASFT_Data, excel_file: Union[str, Path]):
    measurements = measurements_table(data)
    information = information_table(data)

    file_path = Path(excel_file)
    if file_path.exists():
        existing_information_table = pd.read_excel(excel_file, sheet_name="Information")

        if any(information["id_1"].isin(existing_information_table["id_1"])):
            raise Exception("The key already exists in the database.")

    append_dataframe_to_excel(measurements, excel_file, "Measurements")
    append_dataframe_to_excel(information, excel_file, "Information")
