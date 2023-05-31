#!/usr/bin/env python
# coding: utf-8

# In[165]:


# Import libraries

import numpy as np

import pandas
from pandas import ExcelFile

import mip
from mip import Model, xsum, maximize, BINARY

#might need ...
#import math
#import datetime
#import matplotlib.pyplot as plt


# In[166]:


# Acquisizione dei dati dal foglio elettronico

relations = pandas.read_excel('Items.xlsx',sheet_name='Relations')


# In[180]:


# Definizione della lista di elementi

elementi = [{'Name': 'AA Batteries', 'Quantity': 2}, 
            {'Name': 'AAA Batteries', 'Quantity': 2}, 
            {'Name': 'HDMI Cable', 'Quantity': 1}, 
            {'Name': 'Facial Cleanser', 'Quantity': 2}, 
            {'Name': 'Eyeshadow Palette', 'Quantity': 2}, 
            {'Name': 'Aromatherapy Diffuser', 'Quantity': 1}]

# Definizione della matrice di correlazione tra gli elementi
matrice_correlazione =  np.zeros( (len(elementi), len(elementi)) )

for i in range(len(elementi)):
    for j in range(len(elementi)):
        if i != j:
            matrice_correlazione[i][j] = relations.loc[relations['Product'] == elementi[i]['Name'], elementi[j]['Name']].values[0]
# Assicurati che la matrice di correlazione sia simmetrica e con diagonale principale uguale a 0


# In[181]:


matrice_correlazione


# In[182]:


# Definizione del modello

modello = Model()

# Variabile decisionale: Crea una variabile binaria per ogni elemento e matrice per la correlazione
x = [modello.add_var(var_type=BINARY) for _ in elementi]
y = [[modello.add_var(var_type=BINARY) for _ in elementi] for _ in elementi]

# Funzione obiettivo: massimizza la correlazione tra gli elementi del gruppo
modello.objective = maximize(xsum(matrice_correlazione[i][j] * y[i][j] for i in range(len(elementi)) for j in range(len(elementi))))

# Vincoli: Il gruppo deve contenere esattamente 4 elementi, la matrice y dev'essere coerente con l'array degli elementi selezionati
modello += sum(x) == 4

for i in range(len(elementi)):
    for j in range(len(elementi)):
        modello += y[i][j] <= x[i]              #se x[i] non è presente -> y[i][j] = 0
        modello += y[i][j] <= x[j]              #se x[j] non è presente -> y[i][j] = 0
        modello += y[i][j] >= x[i] + x[j] - 1   #se x[i] & x[j] sono presenti -> y[i][j] = 1


# In[183]:


# Ottimizzazione

modello.optimize()

array_ottimale = [x[i].x for i in range(len(elementi))]
gruppo_ottimale = [elementi[i]['Name'] for i in range(len(elementi)) if x[i].x == 1.0]
matrice_ottimale = [[y[i][j].x for j in range(len(elementi))] for i in range(len(elementi))]


# In[184]:


array_ottimale


# In[185]:


gruppo_ottimale


# In[186]:


for i in range(len(elementi)):
    for j in range(len(elementi)):
        print(matrice_ottimale[i][j], end=', ')
    print(' ')


# In[187]:


modello.objective_value


# In[ ]:




