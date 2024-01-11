from pathlib import Path
import pandas as pd

from pdf_processing.ASFT_Data import ASFT_Data
from excel_generation.excel_db import add_data_to_db


if __name__ == "__main__":
    a = ASFT_Data(
        Path("C:/Users/lucas/Desktop/aa2k_ASFT/pdf/AEP/AEP RWY 13 L3_230427_013450.pdf")
    )

    a.runway_length = 2430
    a.runway_starting_position = 20
    path = "C:/Users/lucas/Desktop/aa2k_ASFT/test.xlsx"
    # add_data_to_db(a, path)
    print(a.measurements_with_chainage.head(40))
