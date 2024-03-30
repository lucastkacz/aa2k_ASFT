import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
from tkinter import PhotoImage
from src.excel_generation.excel_db import create_measurement_file
import os
import sys


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class MeasurementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mediciones ASFT")

        icon = PhotoImage(file=resource_path(os.path.join("src", "gui", "logo.png")))
        self.root.iconphoto(True, icon)

        self.setup_frames()
        self.init_fields()
        self.add_made_by_label()

    def setup_frames(self):
        self.input_frame = ttk.Frame(self.root, padding="10")
        self.input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))

        self.button_frame = ttk.Frame(self.root, padding="10")
        self.button_frame.grid(row=1, column=0, sticky=tk.E)

        self.footer_frame = ttk.Frame(self.root, padding="10")
        self.footer_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))

    def add_made_by_label(self):
        # Add a label to the footer frame
        ttk.Label(self.footer_frame, text="Hecho por Lucas Ariel Tkacz \tv1.0.0").grid(
            column=0, row=0, sticky=tk.W
        )

    def init_fields(self):
        # ASFT Measurements Folder
        ttk.Label(self.input_frame, text="Carpeta de mediciones ASFT:").grid(
            column=0, row=0, sticky=tk.W
        )
        self.asft_measurements_folder_var = tk.StringVar()
        ttk.Entry(
            self.input_frame,
            textvariable=self.asft_measurements_folder_var,
            state="readonly",
        ).grid(column=1, row=0)
        ttk.Button(
            self.input_frame,
            text="Browse...",
            command=self.select_asft_measurements_folder,
        ).grid(column=2, row=0)

        # Target Directory
        ttk.Label(self.input_frame, text="Carpeta de destino:").grid(
            column=0, row=1, sticky=tk.W
        )
        self.target_directory_var = tk.StringVar()
        ttk.Entry(
            self.input_frame, textvariable=self.target_directory_var, state="readonly"
        ).grid(column=1, row=1)
        ttk.Button(
            self.input_frame, text="Browse...", command=self.select_target_directory
        ).grid(column=2, row=1)

        # Runway Length
        ttk.Label(self.input_frame, text="Longitud de pista:").grid(
            column=0, row=2, sticky=tk.W
        )
        self.runway_length_var = tk.IntVar()
        ttk.Entry(self.input_frame, textvariable=self.runway_length_var).grid(
            column=1, row=2
        )

        # Runway Starting Position 0118
        ttk.Label(self.input_frame, text="Progresiva de inicio cabecera 01-18:").grid(
            column=0, row=3, sticky=tk.W
        )
        self.runway_starting_position_0118_var = tk.IntVar()
        ttk.Entry(
            self.input_frame, textvariable=self.runway_starting_position_0118_var
        ).grid(column=1, row=3)

        # Runway Starting Position 1936
        ttk.Label(self.input_frame, text="Progresiva de inicio cabecera 19-36:").grid(
            column=0, row=4, sticky=tk.W
        )
        self.runway_starting_position_1936_var = tk.IntVar()
        ttk.Entry(
            self.input_frame, textvariable=self.runway_starting_position_1936_var
        ).grid(column=1, row=4)

        # Operator
        ttk.Label(self.input_frame, text="Operador:").grid(column=0, row=5, sticky=tk.W)
        self.operator_var = tk.StringVar()
        ttk.Entry(self.input_frame, textvariable=self.operator_var).grid(
            column=1, row=5
        )

        # Ambient Temperature
        ttk.Label(self.input_frame, text="Temperatura ambiente:").grid(
            column=0, row=6, sticky=tk.W
        )
        self.ambient_temperature_var = tk.IntVar()
        ttk.Entry(self.input_frame, textvariable=self.ambient_temperature_var).grid(
            column=1, row=6
        )

        # Surface Temperature
        ttk.Label(self.input_frame, text="Temperatura superficie:").grid(
            column=0, row=7, sticky=tk.W
        )
        self.surface_temperature_var = tk.IntVar()
        ttk.Entry(self.input_frame, textvariable=self.surface_temperature_var).grid(
            column=1, row=7
        )

        # Humidity
        ttk.Label(self.input_frame, text="Humedad:").grid(column=0, row=8, sticky=tk.W)
        self.humidity_var = tk.IntVar()
        ttk.Entry(self.input_frame, textvariable=self.humidity_var).grid(
            column=1, row=8
        )

        # Observations
        ttk.Label(self.input_frame, text="Observaciones:").grid(
            column=0, row=9, sticky=tk.W
        )
        self.observations_var = tk.StringVar()
        ttk.Entry(self.input_frame, textvariable=self.observations_var).grid(
            column=1, row=9
        )

        # Submit Button
        ttk.Button(self.button_frame, text="Generar", command=self.submit).grid(
            column=0, row=0
        )

    def select_asft_measurements_folder(self):
        directory = filedialog.askdirectory(
            initialdir=Path.home(), title="Select ASFT Measurements Folder"
        )
        if directory:
            self.asft_measurements_folder_var.set(directory)

    def select_target_directory(self):
        directory = filedialog.askdirectory(
            initialdir=Path.home(), title="Select Target Directory"
        )
        if directory:
            self.target_directory_var.set(directory)

    def validate_integer_multiples_of_10(self, value):
        try:
            ivalue = int(value)
            return ivalue % 10 == 0
        except ValueError:
            return False

    def is_positive_integer(self, value):
        try:
            ivalue = int(value)
            return ivalue > 0
        except ValueError:
            return False

    def clear_all_fields(self):
        # Reset all field variables to their default values
        self.asft_measurements_folder_var.set("")
        self.target_directory_var.set("")
        self.runway_length_var.set(0)
        self.runway_starting_position_0118_var.set(0)
        self.runway_starting_position_1936_var.set(0)
        self.operator_var.set("")
        self.ambient_temperature_var.set(0)
        self.surface_temperature_var.set(0)
        self.humidity_var.set(0)
        self.observations_var.set("")

    def submit(self):
        # Validation for runway length and starting positions
        validation_fields = [
            (self.runway_length_var, "Runway length"),
            (self.runway_starting_position_0118_var, "Runway starting position 0118"),
            (self.runway_starting_position_1936_var, "Runway starting position 1936"),
        ]
        for field, name in validation_fields:
            if not self.validate_integer_multiples_of_10(
                field.get()
            ) or not self.is_positive_integer(field.get()):
                messagebox.showerror(
                    "Error", f"{name} must be a positive integer and a multiple of 10."
                )
                return

        # Validation for ambient and surface temperatures, and humidity
        integer_fields = [
            (self.ambient_temperature_var, "Ambient temperature"),
            (self.surface_temperature_var, "Surface temperature"),
            (self.humidity_var, "Humidity"),
        ]
        for field, name in integer_fields:
            if not self.is_positive_integer(field.get()):
                messagebox.showerror("Error", f"{name} must be an integer.")
                return

        # Assuming all validations pass, call create_measurement_file
        try:
            create_measurement_file(
                asft_measurements_folder=Path(self.asft_measurements_folder_var.get()),
                target_directory=Path(self.target_directory_var.get()),
                runway_length=self.runway_length_var.get(),
                runway_starting_position_0118=self.runway_starting_position_0118_var.get(),
                runway_starting_position_1936=self.runway_starting_position_1936_var.get(),
                operator=self.operator_var.get(),
                ambient_temperature=self.ambient_temperature_var.get(),
                surface_temperature=self.surface_temperature_var.get(),
                humidity=self.humidity_var.get(),
                observations=self.observations_var.get(),
            )
            messagebox.showinfo("Finalizado", "Mediciones cargadas con éxito.")
        except Exception as e:
            messagebox.showerror("Error", str(e))


def main_app():
    root = tk.Tk()
    app = MeasurementApp(root)
    root.mainloop()


if __name__ == "__main__":
    main_app()
