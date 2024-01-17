from pathlib import Path
from excel_generation.excel_db import create_measurement_file


if __name__ == "__main__":
    create_measurement_file(
        Path(r"C:\Users\lucas\Desktop\aa2k_ASFT\pdf\AEP"),
        Path(r"C:\Users\lucas\Desktop\aa2k_ASFT"),
        2500,
        20,
        2480,
        "demasi",
        23,
        42,
        33,
        "sin",
    )
