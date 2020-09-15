import pandas as pd
import geopandas as gpd
import os
import zipfile
import shutil

os.chdir('C:\\Users\\Wallisson\\OneDrive\\Atual\\geopandas')

dir="Dados\\RJ-SETOR\\TEMP"
if not os.path.exists(dir):
    os.makedirs(dir)    
    
for root,dirs,files in os.walk('Dados\\RJ-SETOR\\DADOS'):
    for name in files:
        zip_ref=zipfile.ZipFile('Dados\\RJ-SETOR\\DADOS\\'+name,'r')
        zip_ref.extractall(dir)
        zip_ref.close()
        
setor=pd.concat([gpd.read_file(dir+'//'+item[:-4]+'_setor.shp') for item in files], ignore_index=True)
shutil.rmtree(dir)

censo=pd.read_excel('Dados\\Censo 2010\\RJ\\EXCEL\\Basico_RJ.xls')
setor=gpd.read_file('Dados\\RJ-SETOR\\RJ-SETOR.shp')

#VERIFICAR O TIPO DE DADOS EM CADA COLUNA DO DATAFRAME E DO GEODATAFRAME
censo.dtypes
setor.dtypes

#CONVERTENDO O TIPO
censo['Cod_setor'] = censo['Cod_setor'].astype(str)
censo.dtypes
