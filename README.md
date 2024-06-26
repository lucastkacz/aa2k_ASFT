# ASFT Friction Measurement GUI Parser
## Overview
This GUI application simplifies the extraction, parsing, and creation of Excel files from Airport Surface Friction Tester (ASFT) friction measurement data reports.

## External Libraries Used
1. pypdf
2. pandas
3. openpyxl
4. tkinter

## Usage
### Obtaining ASFT Measurement files
Snippet of a friction measurement corresponding to Aeroparque Internacional Jorge Newbery.
Measurements are always given as tables within a pdf file.
For any specified runway, the number of unique measurements can reach up to 10, varying according to the width of the operating airplane's fuselage.
Example of a single measurement:<br>
![ASFT Measurement example file](main_page/ASFT_Measurement.png)

### Running the ASFT Friction Measurement GUI Parser
Empty fields are filled with requiered information.<br>
![Snippet of the GUI application](main_page/gui.png)

### Created Excel File
Creates a excel workbook containing two worksheets with two worksheets. Información and Mediciones.<br>
![alt text](main_page/Excel_Sample.png)<br>
![alt text](main_page/Data_model.png)

### Measurements are loaded into the friction Power BI Dashboard
![Snippet of the heat map from the Power BI Dashboard](main_page/Mapa_de_calor.png)
![Snippet of the heat map from the Power BI Dashboard](main_page/heat_map_2.png)
![Snippet of the average friction graph from the Power BI Dashboard](main_page/Criticidad.png)
![Snippet of the friction graphs from the Power BI Dashboard](main_page/Friccion.png)
![Snippet of the comparison pane from the Power BI Dashboard](main_page/Comparacion.png)