#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  5 23:26:51 2022

@author: henryandreumarquezsalinas
"""

!pip install swifter
!pip install fuzzywuzzy
!pip install unidecode
!pip install python-Levenshtein

from rapidfuzz import fuzz
from rapidfuzz import process # para cargar librerías de fuzzymatch
import re
import numpy as np
import pandas as pd
import swifter 
import unidecode 
import itertools

# Abriendo los datos

user = os.getlogin()   # Username
data = pd.read_excel(f"Z:/{user}/Documentos/GitHub/First-Repository/data/crime_data/data_administrativa.xlsx", sheet_name='Hoja1')
datacrime = pd.read_excel(f"Z:/henryandreumarquezsalinas/Documentos/GitHub/First-Repository/data/crime_data/data_administrativa.xlsx", sheet_name='Hoja1')

# 1) 

data.columns = map(str.lower, data.columns)

# 2)

def function23(row):
    
    row = row.strip() 
    row = unidecode.unidecode(row)
    row = re.sub('[^a-zA-Z\s]', '',row).lower()
    return row

data['nombre'] = data['nombre'].apply(function23)

# 3)

data['born_date'] = data['born_date'].apply(lambda x: re.sub('(!)|(00:00)|("#%)','',x))
data['date_form'] = pd.to_datetime(data['fecha'], dayfirst = True).dt.strftime('%d/%m/%Y')

# 4)

data['age'] = data['age'].apply(lambda x: re.sub('[^0-9]','',str(x)))

# 5) Crear dummies según el rango del sentenciado en la organización criminal

data["dummy1"] = data['rank'].str.contains(r"banda criminal").map({True: 1, False: 0})
data["dummy2"] = data['rank'].str.contains(r"cabecilla local").map({True: 1, False: 0})
data["dummy3"] = data['rank'].str.contains(r"cabecilla regional").map({True: 1, False: 0})
data["dummy4"] = data['rank'].str.contains(r"sicario").map({True: 1, False: 0})
data["dummy5"] = data['rank'].str.contains(r"extorsion|extorsionador").map({True: 1, False: 0})
data["dummy6"] = data['rank'].str.contains(r"miembro").map({True: 1, False: 0})
data["dummy7"] = data['rank'].str.contains(r"novato|novto|noato|principiante").map({True: 1, False: 0})

# 7)

data['usuario_correo'] = data['correo_abogado'].swifter.apply(lambda x: re.findall('(\w+)\@\.*',str(x)))


