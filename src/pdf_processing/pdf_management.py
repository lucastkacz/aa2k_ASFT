from pathlib import Path
from src.pdf_processing.ASFT_Data import ASFT_Data


def create_asft_objects(directory: Path) -> list[ASFT_Data]:
    """
    Creates ASFT_Data objects for each .pdf file in the given directory.

    :param directory: A Path object representing the directory.
    :return: A list of ASFT_Data objects for .pdf files.
    """
    asft_data_objects = []
    for file_path in directory.glob("*.pdf"):
        if file_path.is_file() and file_path.suffix.lower() == ".pdf":
            asft_data = ASFT_Data(file_path)
            asft_data_objects.append(asft_data)

    return asft_data_objects
