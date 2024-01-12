from pathlib import Path
import pandas as pd

from pdf_processing.ASFT_Data import ASFT_Data
from excel_generation.excel_db import add_data_to_db


if __name__ == "__main__":
    a = ASFT_Data(
        Path(
            "C:/Users/lucas/Desktop/aa2k_ASFT/pdf/AEP/AEP RWY 31  R3_230427_014716.pdf"
        )
    )
    b = ASFT_Data(
        Path("C:/Users/lucas/Desktop/aa2k_ASFT/pdf/AEP/AEP RWY 31 L5_230427_015623.pdf")
    )

    a.runway_length = 2430
    a.runway_starting_position = 2410
    a.operator = "Demasi"
    a.ambient_temperature = 24
    a.surface_temperature = 33
    a.humidity = 66
    a.observations = "sin observaciones"
    b.runway_length = 2430
    b.runway_starting_position = 20
    b.operator = "Demasi"
    b.ambient_temperature = 24
    b.surface_temperature = 33
    b.humidity = 66
    b.observations = "sin observaciones"
    path = "C:/Users/lucas/Desktop/aa2k_ASFT/test.xlsx"
    # add_data_to_db(a, path)
    # add_data_to_db(b, path)
    print(a.friction_measurement_report)
