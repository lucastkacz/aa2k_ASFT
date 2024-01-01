import pandas as pd
import re

import datetime
from pathlib import Path
from typing import Optional, NamedTuple
from pypdf import PdfReader


class ASFT_Data:
    def __init__(self, file_path: Path) -> None:
        self.filename: str = file_path.stem
        self.reader: PdfReader = PdfReader(file_path)

        self._report = None
        self._measurements = None
        self._results = None

        self._iata = None
        self._numbering = None
        self._relative_side = None
        self._separation = None

        self._runway_length = 3000
        self._starting_point = 130

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
    def friction_measurent_report(self) -> pd.DataFrame:
        """
        Returns:
            Configuration Tyre Type      Date and Time Tyre Pressure  Type Water Film Equipment Average Speed  Pilot System Distance Ice Level Runway Length Location
        0  RGL RWY 07 R3      ASTM  23-03-10 11:29:28           2.1  ASTM         ON   SFT0148            66  SUPER         2398.58         0          3300     ASFT
        """
        return self.report_extractor(self.reader)

    @property
    def result_summary(self) -> pd.DataFrame:
        """
        Returns:
          Fric. A Fric. B Fric. C Fric. Max Fric. Min Fric. Avg
        0    0.64    0.68    0.64      0.82      0.42      0.65
        """
        return self.results_extractor(self.reader)

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
        df = self.measurements_extractor()
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

        numbering = 13

        if not self._runway_length or not self._starting_point:
            raise ValueError(
                "Please set the runway length and starting point before calling this function."
            )

        # numbering = int(self.numbering)
        reverse = (
            True if 19 <= numbering <= 36 else False if 1 <= numbering <= 18 else None
        )

        chainage = self._chainage_table(self._runway_length, reversed=reverse)

        start_index = chainage[chainage["Chainage"] == self._starting_point].index[0]

        if start_index + len(self.measurements) > len(chainage):
            raise ValueError(
                "The measurements table overflows the chainage table. Please adjust the starting point or the runway length."
            )

        for col in self.measurements.columns:
            if col not in chainage.columns:
                chainage[col] = 0

            for i, value in enumerate(self.measurements[col]):
                chainage.at[start_index + i, col] = value

        chainage["Color Code"] = chainage["Color Code"].replace(0, "white")

        return chainage

    def measurements_extractor(self):
        """
            Distance  Friction  Speed  Av. Friction 100m Color Code
        0          10      0.69     58               0.00      white
        1          20      0.68     60               0.00      white
        2          30      0.71     62               0.00      white
        3          40      0.71     63               0.00      white
        4          50      0.71     66               0.00      white
        ..        ...       ...    ...                ...        ...
        """
        if self._measurements is None:
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

            self._measurements = pd.DataFrame(
                measurement, columns=["Distance", "Friction", "Speed"]
            )
        return self._measurements

    def report_extractor(self, reader):
        """
           Configuration Tyre Type      Date and Time Tyre Pressure  Type Water Film Equipment Average Speed  Pilot System Distance Ice Level Runway Length Location
        0  RGL RWY 07 R3      ASTM  23-03-10 11:29:28           2.1  ASTM         ON   SFT0148            66  SUPER         2398.58         0          3300     ASFT
        """
        if self._report is None:
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

            self._report = pd.DataFrame([extracted_values])
        return self._report

    def results_extractor(self, reader):
        """
          Fric. A Fric. B Fric. C Fric. Max Fric. Min Fric. Avg
        0    0.64    0.68    0.64      0.82      0.42      0.65
        """
        if self._results is None:
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

            self._results = pd.DataFrame([first_six_values], columns=headers)
        return self._results

    def _parse_date(
        self, date: str, format: str = "%y-%m-%d %H:%M:%S"
    ) -> datetime.datetime:
        """
        Parse a date string and return a datetime object.

        Args:
            date (str): The date string to be parsed.
            format (str, optional): The format of the date string. Defaults to "%y-%m-%d %H:%M:%S".

        Returns:
            datetime.datetime: A datetime object representing the parsed date.
        """
        return datetime.datetime.strptime(date, format)

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
                return "white"
            elif friction_average < 0.5:
                return "red"
            elif friction_average < 0.6:
                return "yellow"
            else:
                return "green"

        assigned_colors = series.apply(assign_color_based_on_friction)

        red_color_mask = assigned_colors == "red"
        white_color_mask = assigned_colors == "white"

        for offset in range(-5, 6):
            shifted_red_mask = assigned_colors.shift(offset) == "red"
            shifted_white_mask = assigned_colors.shift(offset) == "white"
            red_color_mask |= shifted_red_mask & ~shifted_white_mask

        assigned_colors.loc[red_color_mask] = "red"

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

    # def _get_configuration(
    #     self, friction_measurent_report: pd.DataFrame
    # ) -> RunwayConfig:
    #     """
    #     Extract runway configuration details (IATA code, runway numbering, relative_side and separation) from a given string and return
    #     a RunwayConfig object.

    #     Args:
    #         configuration (str): A string containing the runway configuration information.

    #     Returns:
    #         RunwayConfig: A RunwayConfig object with the extracted IATA airport code, runway numbering, relative_side, and separation value.
    #     """
    #     config = friction_measurent_report.loc[0, "Configuration"]

    #     _temp: str = re.search(r"[A-Z][0-9]", config).group()
    #     iata: str = re.search(r"^[A-Z]{3}", config).group()
    #     numbering: str = re.search(r"\b\d{2}\b", config).group()
    #     side: str = _temp[0]
    #     separation: int = int(_temp[1])
    #     return separation


a = ASFT_Data(
    Path("C:/Users/lucas/Desktop/aa2k_ASFT/pdf/AEP/AEP RWY 13 L3_230427_013450.pdf")
)


print(a.measurements_with_chainage)


# TODO: Use a dictionary for cacheing
