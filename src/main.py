import re
import pandas as pd
from pathlib import Path
from pypdf import PdfReader

pdf_path = Path(
    "C:/Users/lucas/Desktop/aa2k_ASFT/pdf/RGL/RGL RWY 07 R3_230310_112928.pdf"
)

reader = PdfReader(pdf_path)


def measurements_extractor(reader):
    pattern = r"(\d+?)(\d{1}\.\d{2})(\d{2})"
    measurement = []
    for page_number in range(len(reader.pages)):
        page = reader.pages[page_number]
        text = page.extract_text()
        if text:
            matches = re.findall(pattern, text)
            for match in matches:
                distance = int(match[0])
                friction = float(match[1])
                speed = int(match[2])
                measurement.append((distance, friction, speed))

    return pd.DataFrame(measurement, columns=["Distance", "Friction", "Speed"])


def report_extractor(reader):
    page = reader.pages[0]
    text = page.extract_text()
    patterns = {
        "Configuration": r"Configuration\s+(.+?)\s+Tyre Type",
        "Tyre Type": r"Tyre Type\s+(.+?)\s*$",
        "Date and Time": r"Date and Time\s+(.+?)\s+Tyre Pressure",
        "Tyre Pressure": r"Tyre Pressure\s+(.+?)\s*$",
        "Type": r"Type\s+(\w+)",
        "Water Film": r"Water Film\s+(.+?)\s*$",
        "Equipment": r"Equipment\s+(\w+)",
        "Average Speed": r"Average Speed\s+(.+?)\s*$",
        "Pilot": r"Pilot\s+(\w+)",
        "System Distance": r"System Distance\s+(.+?)\s*$",
        "Ice Level": r"Ice Level\s+(.+?)\s*$",
        "Runway Length": r"Runway Length\s+(.+?)\s*$",
        "Location": r"Location\s+(.+?)\s*$",
    }

    extracted_values = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.MULTILINE)
        extracted_values[key] = match.group(1) if match else None

    return pd.DataFrame([extracted_values])


def results_extractor(reader):
    page = reader.pages[0]
    text = page.extract_text()
    pattern = r"\d\.\d{2}µ"
    found_values = re.findall(pattern, text)
    first_six_values = [value.replace("µ", "") for value in found_values[:6]]
    headers = ["Fric. A", "Fric. B", "Fric. C", "Fric. Max", "Fric. Min", "Fric. Avg"]
    return pd.DataFrame([first_six_values], columns=headers)


aep = measurements_extractor(reader)
print(aep)
aep = report_extractor(reader)
print(aep)
aep = results_extractor(reader)
print(aep)
