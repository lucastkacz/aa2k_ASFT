import pandas as pd
import re

from pathlib import Path
from pypdf import PdfReader


# TODO: fix chainage table with color code (not reference color names inside the function, delete coumn and recall it)
# TODO: fix report extractor, place everything insied a function
class ASFT_Data:
    def __init__(self, file_path: Path) -> None:
        self.filename: str = file_path.stem
        self.reader: PdfReader = PdfReader(file_path)

        self._cache = {}

        # Manually set properties
        self.runway_length = None
        self.runway_starting_position = None
        self.operator = None
        self.ambient_temperature = None
        self.surface_temperature = None
        self.humidity = None
        self.observations = None

    def __str__(self) -> str:
        """
        Returns:
            AEP 31 BORDE L5_220520_125919
        """
        return f"{self.filename}"

    def __len__(self) -> int:
        """
        Returns:
            Number of rows in the measurements table.
        """
        return len(self.measurements)

    @property
    def friction_measurement_report(self) -> pd.DataFrame:
        """
        Returns:
            Configuration Tyre Type      Date and Time Tyre Pressure  Type Water Film Equipment Average Speed  Pilot System Distance Ice Level Runway Length Location
        0  RGL RWY 07 R3      ASTM  23-03-10 11:29:28           2.1  ASTM         ON   SFT0148            66  SUPER         2398.58         0          3300     ASFT
        """
        return self._report_extractor(self.reader)

    @property
    def result_summary(self) -> pd.DataFrame:
        """
        Returns:
          Fric. A Fric. B Fric. C Fric. Max Fric. Min Fric. Avg
        0    0.64    0.68    0.64      0.82      0.42      0.65
        """
        return self._results_extractor(self.reader)

    @property
    def measurements(self) -> pd.DataFrame:
        """
        Returns:
            Distance Friction Speed  Av. Friction 100m
                10     0.80    61               0.00
                20     0.65    63               0.00
                30     0.53    64               0.00
                40     0.84    67               0.00
                50     0.86    69               0.00
                ...    ...     ...              ...
                1760   0.88    66               0.81
        """
        df = self._measurements_extractor()
        df["Av. Friction 100m"] = self._rolling_average(df["Friction"])
        df["Color Code"] = self._color_assignment(df["Av. Friction 100m"])
        return df

    @property
    def measurements_with_chainage(self) -> pd.DataFrame:
        """
        Aligns the measurements table with the corresponding chainage of the runway, measured from left to right.

        This function takes runway numbering and runway length as inputs, calculates the chainage table, and then aligns
        the measurements data with the corresponding chainage values based on the starting point. The chainage values are
        measured from left to right, starting from the runway numbers that are between 01 and 18. The resulting DataFrame
        contains the Key, chainage, and measurements columns.

        Args:
            data (ASFT_Data): An instance of the ASFT_Data class, which contains the runway numbering, key, and measurements.
            runway_length (int): The total length of the runway, which should be a positive integer value.
            starting_point (int): The chainage value where the measurements data should start aligning, referenced
                                from the runway numbers between 01 and 18.

        Returns:
                Chainage  Distance  Friction  Speed  Av. Friction 100m
            0        2200         0      0.00      0                0.0
            1        2190         0      0.00      0                0.0
            2        2180         0      0.00      0                0.0
            3        2170        10      0.84     62                0.0
            4        2160        20      0.82     63                0.0
            ..        ...       ...       ...    ...                ...
            216        40         0      0.00      0                0.0

        Raises:
            ValueError: If the measurements table overflows the chainage table. This error suggests adjusting the starting
                        point or the runway length.


            |=============|===================================================================|=============|
            | -> -> -> -> |11   ===   ===   ===   ===   [  RWY  ]   ===   ===   ===   ===   29| <- <- <- <- |
            |=============|===================================================================|=============|

            |...............................................................................................| chainage
            [ ORIGIN ]                                                                             [ LENGTH ]


                          |.................................................................................| starting point from header 11
                          [ START ] -> -> -> -> -> -> -> -> -> -> -> -> -> ->-> -> -> -> -> -> -> -> -> -> ->


                                                                                              |.............| starting point from header 29
            <- <- <- <- <- <- <- <- <- <- <- <- <- <- <- <- <- <- <- <- <- <- <- <- <- <- <-  [ START ]

        """
        if self.runway_length is None or self.runway_starting_position is None:
            raise ValueError(
                "Please set the runway length and starting point before calling this function."
            )
        numbering = int(self.configuration.loc[0, "numbering"])
        reverse = (
            True if 19 <= numbering <= 36 else False if 1 <= numbering <= 18 else None
        )

        chainage = self._chainage_table(self.runway_length, reversed=reverse)

        start_index = chainage[
            chainage["Chainage"] == self.runway_starting_position
        ].index[0]

        if start_index + len(self.measurements) > len(chainage):
            raise ValueError(
                "The measurements table overflows the chainage table. Please adjust the starting point or the runway length."
            )

        float_columns = [
            "Friction",
            "Av. Friction 100m",
        ]
        for col in float_columns:
            if col in chainage.columns:
                chainage[col] = chainage[col].astype(float)
            elif col in self.measurements.columns:
                chainage[col] = 0.0
        for col in self.measurements.columns:
            if col not in chainage.columns:
                chainage[col] = "blanco" if col == "Color Code" else 0

            for i, value in enumerate(self.measurements[col]):
                chainage.at[start_index + i, col] = value

        headers = [
            "Chainage",
            "Distance",
            "Friction",
            "Av. Friction 100m",
            "Speed",
            "Color Code",
        ]
        chainage = chainage[headers]

        return chainage

    @property
    def configuration(self) -> pd.DataFrame:
        return self._get_configuration()

    @property
    def id_1(self) -> str:
        return self.filename.replace(" ", "")

    @property
    def id_2(self) -> str:
        return (
            f"{self.configuration.loc[0, 'iata']}"
            f"{self.configuration.loc[0, 'runway']}"
        )

    def _measurements_extractor(self):
        """
            Distance  Friction  Speed  Av. Friction 100m Color Code
        0          10      0.69     58               0.00      white
        1          20      0.68     60               0.00      white
        2          30      0.71     62               0.00      white
        3          40      0.71     63               0.00      white
        4          50      0.71     66               0.00      white
        ..        ...       ...    ...                ...        ...
        """

        key = "measurements"
        if key not in self._cache:
            pattern = r"(\d+?)(\d{1}\.\d{2})(\d{2})"
            measurement = []
            for page_number in range(len(self.reader.pages)):
                page = self.reader.pages[page_number]
                text = page.extract_text()
                if text:
                    matches = re.findall(pattern, text)
                    for match in matches:
                        distance = int(match[0])
                        friction = float(match[1])
                        speed = int(match[2])
                        measurement.append((distance, friction, speed))

            self._cache[key] = pd.DataFrame(
                measurement, columns=["Distance", "Friction", "Speed"]
            )
        return self._cache[key]

    def _report_extractor(self, reader):
        """
           Configuration Tyre Type      Date and Time Tyre Pressure  Type Water Film Equipment Average Speed  Pilot System Distance Ice Level Runway Length Location
        0  RGL RWY 07 R3      ASTM  23-03-10 11:29:28           2.1  ASTM         ON   SFT0148            66  SUPER         2398.58         0          3300     ASFT
        """

        key = "report"
        if key not in self._cache:
            page = reader.pages[0]
            text = page.extract_text()
            patterns = {
                # "Configuration": r"Configuration\s+(.+?)\s+Tyre Type",
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

            df = pd.DataFrame([extracted_values])
            df["Date and Time"] = pd.to_datetime(
                df["Date and Time"], format="%y-%m-%d %H:%M:%S"
            )

            start = text.find("Configuration") + len("Configuration ")
            end = text.find("Tyre Type")
            configuration_text = text[start:end].replace("\n", " ").strip()

            df["Configuration"] = configuration_text

            self._cache[key] = df
        return self._cache[key]

    def _results_extractor(self, reader):
        """
          Fric. A Fric. B Fric. C Fric. Max Fric. Min Fric. Avg
        0    0.64    0.68    0.64      0.82      0.42      0.65
        """

        key = "results"
        if key not in self._cache:
            page = reader.pages[0]
            text = page.extract_text()
            pattern = r"\d\.\d{2}µ"
            found_values = re.findall(pattern, text)
            first_six_values = [value.replace("µ", "") for value in found_values[:6]]
            headers = [
                "Fric. A",
                "Fric. B",
                "Fric. C",
                "Fric. Max",
                "Fric. Min",
                "Fric. Avg",
            ]

            self._cache[key] = pd.DataFrame([first_six_values], columns=headers)
        return self._cache[key]

    def _rolling_average(
        self,
        series: pd.Series,
        window_size: int = 10,
        center: bool = True,
        digits: int = 2,
    ) -> pd.Series:
        """
        Calculate the rolling average of a given pandas series and round the result to a specified number of decimal places.

        Args:
            series (pd.Series): The input pandas series for which the rolling average is to be calculated.
            window_size (int, optional): The window size for calculating the rolling average. Defaults to 10.
            center (bool, optional): Whether to center the window around the current row or use a trailing window. Defaults to True.
            digits (int, optional): The number of decimal places to round the result to. Defaults to 2.

        Returns:
            pd.Series: A pandas series with the rounded rolling average values.
        """
        return (
            series.rolling(window=window_size, center=center)
            .mean()
            .fillna(0)
            .round(digits)
        )

    def _color_assignment(self, series: pd.Series) -> pd.Series:
        """
        Assign a color to each friction average in a given pandas series based on the friction average,
        and propagate 'red' color to a window of 5 positions before and after each 'red' friction average,
        omitting rows where the color is 'white', following OACI and FAA recommendations.

        The color assignment rules are as follows:
        - 'white' for friction average equal to 0.0
        - 'red' for friction average less than 0.5
        - 'yellow' for friction average less than 0.6 but not less than 0.5
        - 'green' otherwise

        Args:
            series (pd.Series): The input pandas series of friction averages for which the color is to be assigned.

        Returns:
            pd.Series: A pandas series with assigned colors, where 'red' color is propagated
            to 5 positions before and after each 'red' friction average, omitting 'white' rows.
        """

        def assign_color_based_on_friction(friction_average):
            if friction_average == 0.0:
                return "blanco"
            elif friction_average < 0.5:
                return "rojo"
            elif friction_average < 0.6:
                return "amarillo"
            else:
                return "verde"

        assigned_colors = series.apply(assign_color_based_on_friction)

        red_color_mask = assigned_colors == "rojo"
        white_color_mask = assigned_colors == "blanco"

        for offset in range(-5, 6):
            shifted_red_mask = assigned_colors.shift(offset) == "rojo"
            shifted_white_mask = assigned_colors.shift(offset) == "blanco"
            red_color_mask |= shifted_red_mask & ~shifted_white_mask

        assigned_colors.loc[red_color_mask] = "rojo"

        return assigned_colors

    def _chainage_table(
        self, runway_length: int, step: int = 10, reversed: bool = False
    ) -> pd.DataFrame:
        """
        Create a DataFrame containing chainage values at a specified step interval up to a given runway_length.

        Args:
            runway_length (int): The total length of the runway, which should be a positive integer value.
            step (int, optional): The step interval for generating chainage values. Defaults to 10.
            reversed (bool, optional): Whether to reverse the order of the resulting DataFrame rows. Defaults to False.

        Returns:
            pd.DataFrame: A pandas DataFrame containing a single column named "chainage" with chainage values at the
            specified step intervals, starting from 0 and ending with the runway_length value.
        """
        chainage = list(range(0, runway_length + 1, step))
        if chainage[-1] != runway_length:
            chainage.append(runway_length)

        df = pd.DataFrame(chainage, columns=["Chainage"])

        if reversed:
            df = df[::-1].reset_index(drop=True)

        return df

    def _get_configuration(self):
        key = "configuration"
        if key not in self._cache:
            config = self.friction_measurement_report.loc[0, "Configuration"]
            _temp: str = re.findall(r"[A-Z][0-9]", config)[-1]
            iata: str = re.search(r"^[A-Z]{3}", config).group()
            numbering: str = re.search(r"\d{2}\b", config).group()
            relative_side: str = _temp[0]
            separation: int = int(_temp[1])

            def get_runway_designation(runway: str) -> str:
                runway_num = int(runway)
                opposite_runway_num = (
                    runway_num + 18 if runway_num <= 18 else runway_num - 18
                )
                first_runway, second_runway = sorted([runway_num, opposite_runway_num])
                formatted_first_runway = f"{first_runway:02d}"
                formatted_second_runway = f"{second_runway:02d}"
                runway_designation = (
                    f"{formatted_first_runway}-{formatted_second_runway}"
                )
                return runway_designation

            def get_absolute_side(numbering: str, relative_side: str) -> str:
                runway_number = int(numbering)
                if 1 <= runway_number <= 18:
                    absolute_side = relative_side
                else:
                    absolute_side = "L" if relative_side == "R" else "R"
                return absolute_side

            self._cache[key] = pd.DataFrame(
                [
                    {
                        "iata": iata,
                        "numbering": numbering,
                        "runway": get_runway_designation(numbering),
                        "absolute side": get_absolute_side(numbering, relative_side),
                        "relative side": relative_side,
                        "separation": separation,
                    }
                ]
            )
        return self._cache[key]


if __name__ == "__main__":
    a = ASFT_Data(
        Path("C:/Users/lucas/Desktop/aa2k_ASFT/pdf/AEP/AEP RWY 13 L3_230427_013450.pdf")
    )

    a.runway_length = 2430
    a.runway_starting_position = 20

    print(a.friction_measurement_report.loc[0, "Date and Time"])
