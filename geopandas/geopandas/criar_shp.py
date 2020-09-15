import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import os

os.chdir('C:\\Users\\Wallisson\\OneDrive\\Atual\\geopandas')
### LENDO

rj=gpd.read_file("Dados\\RJ\\33MUE250GC_SIR.shp")
rj.plot(color="white",edgecolor="black",figsize=(15,8))


## MODIFICANDO
#SELECIONANDO ATRIBUTOS
rj=rj[rj["NM_MUNICIP"]== 'RIO DE JANEIRO']
rj.plot(color="orange",edgecolor="black",figsize=(15,8))

dir="Dados\\RJ-MUNIP\\"
if not os.path.exists(dir):
    os.makedirs(dir)
rj.to_file(dir+'//RJ-MUNIC.shp')

#READ FILE
rj=gpd.read_file('Dados\\RJ-MUNIP\\RJ-MUNIC.shp')


dados=pd.read_table("Dados\\dados.txt")
geometry=[Point(x) for x in zip(dados.Longitude,dados.Latitude)]
crs={'proj':'latlong','ellps':'WGS84','datum':'WGS84','no_def':True}
geo_dados=gpd.GeoDataFrame(dados,crs=crs,geometry=geometry)

dir="Dados\\RJ-DATASET\\"
if not os.path.exists(dir):
    os.makedirs(dir)
geo_dados.to_file(dir+'//dataset.shp')


#MUDAR A PROJEÇÃO
crs='+proj=utm +zone=23 +south +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=km +no_defs' #SIRGAS2000 UTM23S
rj=rj.to_crs('+proj=utm +zone=23 +south +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=km +no_defs')
geo_dados=geo_dados.to_crs('+proj=utm +zone=23 +south +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=km +no_defs')
base= rj.plot(color="white", edgecolor="black",figsize=(15,8))
geo_dados.plot(ax=base,figsize=(15,8),alpha=0.2)

#VER SE UM PONTO ESTÁ DENTRO DE UM SHAPEFILE
geo_dados.iloc[0].geometry.within(rj.iloc[0].geometry)
#VER SE UM SHAPEFILE CONTÉM UM PONTO
rj.iloc[0].geometry.contains(geo_dados.iloc[0].geometry)

#SELECIONA OS PONTOS DO SHAPEFILE QUE ESTÃO DENTRO DO OUTRO SHAPEFILE
geo_dados=geo_dados[geo_dados['geometry'].within(rj.iloc[0].geometry)]
dir="Dados\\RJ-DATASET\\"
geo_dados.to_file(dir+'//dataset.shp')

#READ FILES
geo_dados=gpd.read_file("Dados\\RJ-DATASET\\dataset.shp")



#Distâncias
metro=gpd.read_file("Dados\\Transporte\\Metro\\Estações_Metrô.shp")
metro=metro.to_crs('+proj=utm +zone=23 +south +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=km +no_defs')
distances = metro.distance(geo_dados.iloc[0].geometry)
geo_dados['Dist_Metro'] = geo_dados['geometry'].apply(lambda x: metro.distance(x).min())

#Dados Trem
trem=gpd.read_file("Dados\\Transporte\\Trem\\Estações_Trem.shp")
trem=trem.to_crs('+proj=utm +zone=23 +south +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=km +no_defs')
trem=trem[trem['geometry'].within(rj.iloc[0].geometry)]

base= rj.plot(color="white", edgecolor="black",figsize=(15,8))
geo_dados.plot(ax=base,color="orange",alpha=0.2)
metro.plot(ax=base,color='black',markersize=80)
trem.plot(ax=base,color='red',markersize=80)

#BRT
BRT=gpd.read_file("Dados\\Transporte\\BRT\\Estações_BRT.shp")
BRT=BRT.to_crs('+proj=utm +zone=23 +south +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=km +no_defs')
base= rj.plot(color="white", edgecolor="black",figsize=(15,8))
geo_dados.plot(ax=base,color="orange",alpha=0.2)
metro.plot(ax=base,color='black',markersize=80)
trem.plot(ax=base,color='red',markersize=80)
BRT.plot(ax=base,color='blue',markersize=80)


#CONCATENAR GEOMETRIAS
transporte=pd.concat([trem.geometry,metro.geometry,BRT.geometry],ignore_index=True)
geo_dados['Dist_Transporte']=geo_dados['geometry'].apply(lambda x: transporte.distance(x).min())
geo_dados.to_file("Dados\\RJ-DATASET\\dataset.shp")

#PRAIAS
praias=gpd.read_file("Dados\\Vegetação e Uso do Solo\\Cobertura_Vegetal_e_Uso_da_Terra_2016.shp")
praias=praias.to_crs('+proj=utm +zone=23 +south +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=km +no_defs')
praias['legenda'].value_counts()
praias=praias[praias['legenda']=='Praia']
base= rj.plot(color="white", edgecolor="black",figsize=(15,8),alpha=0.2)
praias.plot(ax=base,color="black")

geo_dados['Dist_Praia']=geo_dados['geometry'].apply(lambda x: praias.distance(x).min())
geo_dados.to_file("Dados\\RJ-DATASET\\dataset.shp")


























