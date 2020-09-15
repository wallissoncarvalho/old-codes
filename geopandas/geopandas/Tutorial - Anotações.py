'''Anotações 1: Lendo, Modificando e Escrevendo arquivos'''

import geopandas as gpd
import os
#Ler um arquivo
os.chdir('C:\\Users\\Wallisson\\OneDrive\\Atual\\geopandas')
rj=gpd.read_file("Dados\\municipios-rj.shp")


#SELECIONANDO APENAS AS GEOMETRIAS DO MUNICÍPIO DO RIO DE JANEIRO E ARIPÉ
rj=rj[rj['NM_MUNICIP'].isin(['RIO DE JANEIRO','APERIBÉ'])]

#SELECIONANDO TODOS OS MUNICÍPIOS EXCETO O DO RIO DE JANEIRO E O ARIPÉ
rj=rj[rj['NM_MUNICIP'].isin(['RIO DE JANEIRO','APERIBÉ'])==False]


#CRIANDO UM SHAPEFILE COM APENAS O MUNICÍPIO DO RIO DE JANEIRO
rj_municipio=rj[rj['NM_MUNICIP'].isin(['RIO DE JANEIRO'])]
rj.to_file('Dados//rj-municipio.shp')




''' Anotações 2: Criando um shapefile a partir de um arquivo de texto '''
import pandas as pd
import geopandas as gpd

#IMPORTANDO O ARQUIVO DE TEXTO COMO UM DATAFRAME
dados=pd.read_table("Dados\\dados.txt") #Dados geoespaciais (pontos) de imóveis para venda no estado do RJ incluindo área

#VISUALIZANDO INFORMAÇÕES DE COLUNAS
dados.info()

#VISUALIZANDO INFORMAÇÕES ESTATÍSTICAS (RESUMO)
estat=dados.describe()

