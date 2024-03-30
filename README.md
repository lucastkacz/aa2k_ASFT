# ASFT Friction Measurement GUI Parser
## Overview
This GUI application is designed to streamline the process of extracting, parsing, and creating excel files from ASFT friction measurement data reports.

## External Libraries Used
1. pypdf
2. pandas
3. openpyxl
4. tkinter

## Usage
### Obtaining ASFT Measurement files
Snippet of measurement corresponding to Aeroparque Internacional Jorge Newbery
![alt text](github/ASFT_Measurement.png)

### Running the ASFT Friction Measurement GUI Parser
Empty fields are filled with requiered information
![alt text](github/gui.png)

### Created Excel File
Creates a excel workbook containing two worksheets with the following columns
![alt text](github/Excel_Sample.png)
1. Mediciones
   1. id_1
   2. progresiva
   3. distancia
   4. fricción
   5. velocidad
   6. prom. fricción 100m
   7. criticidad
2. Información
   1. id_1
   2. id_2
   3. fecha
   4. horario
   5. iata
   6. cabecera
   7. lado relativo
   8. lado absoluto
   9. separación
   10. pista
   11. velocidad promedio
   12. fric_A
   13. fric_B
   14. fric_C
   15. fric_max
   16. fric_min
   17. fric_prom
   18. longitud de pista
   19. inicio de medición
   20. equipo
   21. piloto
   22. nivel de hielo
   23. presión de neumático
   24. película de agua
   25. distancia sistema
   26. operador
   27. temperatura ambiente
   28. temperatura de pista
   29. humedad
   30. observaciones

### Measurements are loaded into the friction Power BI Dashboard
![alt text](github/Mapa_de_calor.png)
![alt text](github/Friccion.png)