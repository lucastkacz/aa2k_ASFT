from pdf_processing.ASFT_Data import ASFT_Data
import pandas as pd
from pathlib import Path
from typing import Optional, Union
from excel_generation.functions.excel_operations import append_dataframe_to_excel


def measurements_table(data: ASFT_Data) -> pd.DataFrame:
    measurements = data.measurements_with_chainage
    measurements_df = pd.DataFrame(
        {
            "id_1": data.id_1,
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
            "cabecera": [data.configuration.loc[0, "numbering"]],
            "lado relativo": [data.configuration.loc[0, "relative side"]],
            "lado absoluto": [data.configuration.loc[0, "absolute side"]],
            "separación": [data.configuration.loc[0, "separation"]],
            "pista": [data.configuration.loc[0, "runway"]],
            "velocidad promedio": [
                data.friction_measurement_report.loc[0, "Average Speed"]
            ],
            "fric_A": [data.result_summary.loc[0, "Fric. A"]],
            "fric_B": [data.result_summary.loc[0, "Fric. B"]],
            "fric_C": [data.result_summary.loc[0, "Fric. C"]],
            "fric_max": [data.result_summary.loc[0, "Fric. Max"]],
            "fric_min": [data.result_summary.loc[0, "Fric. Min"]],
            "fric_prom": [data.result_summary.loc[0, "Fric. Avg"]],
            "longitud de pista": [data.runway_length],
            "inicio de medición": [data.runway_starting_position],
            "equipo": [data.friction_measurement_report.loc[0, "Equipment"]],
            "piloto": [data.friction_measurement_report.loc[0, "Pilot"]],
            "nivel de hielo": [data.friction_measurement_report.loc[0, "Ice Level"]],
            "presión de neumático": [
                data.friction_measurement_report.loc[0, "Tyre Pressure"]
            ],
            "película de agua": [data.friction_measurement_report.loc[0, "Water Film"]],
            "distancia sistema": [
                data.friction_measurement_report.loc[0, "System Distance"]
            ],
            "operador": [data.operator],
            "temperatura ambiente": [data.ambient_temperature],
            "temperatura de pista": [data.surface_temperature],
            "humedad": [data.humidity],
            "observaciones": [data.observations],
        }
    )


def add_data_to_db(data: ASFT_Data, excel_file: Union[str, Path]):
    measurements = measurements_table(data)
    information = information_table(data)

    file_path = Path(excel_file)
    if file_path.exists():
        existing_information_table = pd.read_excel(excel_file, sheet_name="Información")

        if any(information["id_1"].isin(existing_information_table["id_1"])):
            raise Exception("El id ya se encuentra en la base de datos.")

    append_dataframe_to_excel(measurements, excel_file, "Mediciones")
    append_dataframe_to_excel(information, excel_file, "Información")
