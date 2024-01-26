from pathlib import Path
from excel_generation.excel_db import create_measurement_file


if __name__ == "__main__":
    create_measurement_file(
        asft_measurements_folder=Path(r"C:\Users\lucas\Desktop\aa2k_ASFT\pdf\MDZ"),
        target_directory=Path(r"C:\Users\lucas\Desktop\aa2k_ASFT"),
        runway_length=3000,
        runway_starting_position_0118=10,
        runway_starting_position_1936=2900,
        operator="demasi",
        ambient_temperature=23,
        surface_temperature=42,
        humidity=33,
        observations="sin",
    )
