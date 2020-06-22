# -*- coding: utf-8 -*-
"""
Created on Sat Jun 22 16:05:37 2019

@author: walli
"""

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import fiona
fiona.supported_drivers['KML'] = 'rw'

dados=pd.read_csv('C:\\Users\\walli\\Desktop\\Medições\\Corrigido\\20051021184647.sum',encoding='unicode_escape')

  
    
def convert_latitude(x):
    if len(x)==15:
        x=(int(x[2:3])+int(x[5:7])/60+float(x[9:14])/3600)*-1
    elif len(x)==14:
        x=(int(x[2:3])+int(x[5:7])/60+float(x[9:13])/3600)*-1
    return x

dados['Latitude (deg)']=dados['Latitude (deg)'].apply(lambda x:convert_latitude(x))

def convert_longitude(x):
    if len(x)==14:
        x=(int(x[1:3])+int(x[5:7])/60+float(x[9:13])/3600)*-1
    elif len(x)==15:
        x=(int(x[1:3])+int(x[5:7])/60+float(x[9:14])/3600)*-1
    return x

dados['Longitude (deg)']=dados['Longitude (deg)'].apply(lambda x:convert_longitude(x))

shape_pontos=[Point(x) for x in zip(dados['Longitude (deg)'],dados['Latitude (deg)'])]
crs={'proj':'latlong','ellps':'WGS84','datum':'WGS84','no_def':True} #SC WGS 8
shape_pontos=gpd.GeoDataFrame(crs=crs,geometry=shape_pontos)
shape_pontos['Sample #']=dados['Sample #']
shape_pontos['Track (m)']=dados['Track (m)']

shape_pontos.to_file('C:\\Users\\walli\\Desktop\\Medições\\Corrigido\\20051021195504.shp')