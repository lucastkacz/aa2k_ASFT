from pathlib import Path
from excel_generation.excel_db import create_measurement_file


def manual_interface():
    create_measurement_file(
        asft_measurements_folder=Path(
            r"C:\Users\lucas\Desktop\aa2k_ASFT\pdf\AEP\28 de febrero"
        ),
        target_directory=Path(r"C:\Users\lucas\Desktop\aa2k_ASFT"),
        runway_length=2280,
        runway_starting_position_0118=110,
        runway_starting_position_1936=2180,
        operator="Demasi",
        ambient_temperature=23,
        surface_temperature=42,
        humidity=66,
        observations="Sin Observaciones",
    )


if __name__ == "__main__":
    manual_interface()
