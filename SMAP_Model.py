"""
SMAP - Monthly Model
@author: Wallisson
"""
import os
import calendar
import xarray as xr 
import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
import numpy as np

os.chdir('D:\\OneDrive\\Atual\\GAMA\\SMAP')


def pixels_shape(dados,shape_dir,shape_num):
    area=gpd.read_file(shape_dir)
    area2 = gpd.read_file(shape_dir)
    area2.pop('geometry')
    print(area2)
    for coord_name in list(dados.coords._names):
        if coord_name=='latitude':
            dados=dados.dropna(dim='latitude',how='all')
            dados=dados.dropna(dim='longitude',how='all')
            latitudes=dados.coords['latitude'].values
            longitudes=dados.coords['longitude'].values
            if longitudes.max()>180:
                dados['longitude'] = ((dados.longitudes + 180) % 360 - 180).sortby(dados.longitudes)    
            x,y=[],[]
            for lati in latitudes:
                longitudes=dados.sel(latitude=lati)              
                longitudes=longitudes.dropna(dim='longitude',how='all')
                longitudes=longitudes.coords['longitude'].values
                for long in longitudes:
                    x.append(long)
                    y.append(lati)    
            pontos=[Point(x) for x in zip(x,y)]
            crs={'proj':'latlong','ellps':'WGS84','datum':'WGS84','no_def':True} #SC WGS 8
            pixels=gpd.GeoDataFrame(crs=crs,geometry=pontos)            
            pixels=pixels[pixels.geometry.within(area.geometry[shape_num])]
            x,y=[],[]
            serie=pd.DataFrame()
            for pixel in pixels['geometry']:
                lat=pixel.y
                lon=pixel.x
                x.append(lon)
                y.append(lat)
                serie=pd.concat([serie,dados.sel(latitude=pixel.y,longitude=pixel.x).to_dataframe()])
                pixels_df=pd.DataFrame({'Latitude':y,'Longitude':x})
        elif coord_name=='lat':
            dados=dados.dropna(dim='lat',how='all')
            dados=dados.dropna(dim='lon',how='all')
            latitudes=dados.coords['lat'].values
            longitudes=dados.coords['lon'].values
            if longitudes.max()>180:
                dados['lon'] = ((dados.lon + 180) % 360 - 180).sortby(dados.lon)
            x,y=[],[]
            for lati in latitudes:
                longitudes=dados.sel(lat=lati)
                longitudes=longitudes.dropna(dim='lon',how='all')
                longitudes=longitudes.coords['lon'].values
                for long in longitudes:
                    x.append(long)
                    y.append(lati)    
            pontos=[Point(x) for x in zip(x,y)]
            crs={'proj':'latlong','ellps':'WGS84','datum':'WGS84','no_def':True} #SC WGS 8
            pixels=gpd.GeoDataFrame(crs=crs,geometry=pontos)            
            pixels=pixels[pixels.geometry.within(area.geometry[shape_num])]
            x,y=[],[]
            for pixel in pixels['geometry']:
                x.append(pixel.x)
                y.append(pixel.y)
                serie=pd.concat([serie,dados.sel(lat=pixel.y,lon=pixel.x).to_dataframe()])
                serie.groupby()
                pixels_df=pd.DataFrame({'Latitude':y,'Longitude':x})                 
    serie=serie.groupby(serie.index).mean()
    return pixels_df,serie

def vazao(codigo):
    #PARTE 1 - IMPORTA OS DADOS
    df=pd.read_csv('VAZAO_'+str(codigo)+'.csv', sep=';', skiprows=14, header=None)
    df[2] =  pd.to_datetime(df[2], format='%d/%m/%Y')
    df=df.loc[df.groupby(2)[1].idxmax()] #REMOVE OS DADOS DUPLICADOS QUE COM CONSISTÊNCIA 1
    df.index=df[2]
    #PARTE 2 TRANSFORMA OS DADOS PARA SÉRIE CONTÍNUA COM UMA COLUNA
    lista_series_mensais=[]
    for data in list(df[2]):
        n,ultimo_dia=calendar.monthrange(data.year,data.month)
        mes=pd.date_range(data,periods=ultimo_dia, freq='D')
        serie_linha=pd.Series(df.loc[data,16:15+ultimo_dia], name='Dados')
        serie = pd.Series(list(serie_linha),index = mes)
        lista_series_mensais.append(serie)
    serie_completa=pd.concat(lista_series_mensais)
    serie_completa=serie_completa.apply(lambda x: float(x.replace(',','.')) if isinstance(x,str) else x)
    serie_completa=serie_completa.sort_index()
    data_index = pd.date_range(serie_completa.index[0], serie_completa.index[-1], freq='D')
    serie_completa=serie_completa.reindex(data_index)
    return serie_completa.sort_index()

def retorna_serie1(var,shape_num):
    serie_mes=pd.DataFrame()
    for file in os.listdir('NETCDF'):
        if file[0:len(var)]==var:
            dados=xr.open_dataset('NETCDF//'+file)
            pixels_df,serie = pixels_shape(dados,'shapes\\reconcavo.shp',shape_num)
            serie_mensal=serie.groupby([lambda x: x.year, lambda x: x.month]).sum()
            serie_mes=pd.concat([serie_mes,serie_mensal])
    serie_mes=serie_mes[var].to_frame()
    return serie_mes

def retorna_serie2(var,shape_num):
    serie_mes=pd.DataFrame()
    for file in os.listdir('NETCDF'):
        if file[0:len(var)]==var:
            dados=xr.open_dataset('NETCDF//'+file)
            pixels_df,serie = pixels_shape(dados,'shapes\\reconcavo.shp',shape_num)
            serie_mensal=serie.groupby([lambda x: x.year, lambda x: x.month]).mean()
            serie_mes=pd.concat([serie_mes,serie_mensal])
    serie_mes=serie_mes[var].to_frame()
    return serie_mes


#Parte 1: Dados de Entrada
Prec=retorna_serie1('prec',4)
ET=retorna_serie1('ETo',4)[:-19]
#RH=retorna_serie2('RH',0)[:-19]
#Rs=retorna_serie2('Rs',0)[:-19]
#Tmax=retorna_serie2('Tmax',0)[:-19]
#Tmin=retorna_serie2('Tmin',0)[:-19]
#u2=retorna_serie2('u2',0)[:-19]
dados=pd.concat([Prec,ET],axis=1)


#Parte 2: Parâmetros 
#Parâmetros de inicialização
    # TUin -> Teor de umidade do solo inicial (%)
    # Ebin -> Escoamento de base inicial (mm)  
INI = {'TUin':(74/100),'Ebin':(0.38)} 

#Parâmetros regionais
    # Sat -> Capacidade de saturação do solo(mm)
    # Pes -> Parâmetro de Escoamento Superficial (adimensional)
    # Crec -> Coeficiente de recarga (adimensional)
    # KK -> constante de recessão (1/mês), t.q. -> KK = 0.5^(1/KKT)
    # KKT -> número de meses em que a vazão cai para a metade do seu valor
    # Area da Bacia (km²)   
PRM = {'Sat':2660,'Pes':7.1,'Crec':(0.81/100),'KK':(0.5**(1/6)),'Area':2860.0}


#Função cálculo SMAP, para parâmetros já calibrados
def smap(INI,PRM,Prec,ET): #INI,PRM são dicionário, Prec e ET são listas
    Rsolo,TU,Es,Er,Rec,Rsub,Eb,vazao_calc=[],[],[],[],[],[],[],[]
    Rsolo_inicial = INI['TUin']*PRM['Sat']
    Rsub_inicial = (INI['Ebin']/(1-PRM['KK'])/PRM['Area']*2630)
    
    for i in range(len(ET)):
        if i==0:
            TU.append(Rsolo_inicial/PRM['Sat'])
            Es.append((TU[i]**PRM['Pes'])*Prec[i])
            Er.append(TU[i]*ET[i])
            Rec.append(PRM['Crec']*(TU[i]**4)*Rsolo_inicial)
            Eb.append((1-PRM['KK'])*Rsub_inicial)
            
            Rsolo.append(Rsolo_inicial+Prec[i]-Es[i]-Er[i]-Rec[i])
            Rsub.append(Rsub_inicial+Rec[i]-Eb[i])
            vazao_calc.append((Es[i]+Eb[i])*PRM['Area']/2630)
        else:
            TU.append(Rsolo[i-1]/PRM['Sat'])
            Es.append((TU[i]**PRM['Pes'])*Prec[i])
            Er.append(TU[i]*ET[i])
            Rec.append(PRM['Crec']*(TU[i]**4)*Rsolo[i-1])
            Eb.append((1-PRM['KK'])*Rsub[i-1])
            
            Rsolo.append(Rsolo[i-1]+Prec[i]-Es[i]-Er[i]-Rec[i])
            Rsub.append(Rsub[i-1]+Rec[i]-Eb[i])
            vazao_calc.append((Es[i]+Eb[i])*PRM['Area']/2630)
    Es=[round(x,2) for x in Es]
    Eb=[round(x,2) for x in Eb]    
    vazao_calc=[round(x,2) for x in vazao_calc]
    calculado=pd.DataFrame({'Es':Es,'Eb':Eb,'Vazao':vazao_calc})
    return calculado


#Função cálculo do SMAP com adição de séries sintéticas de pricipitação e evapotranspiração
def analise(INI,PRM,dados):
    media=dados['prec'].groupby(dados['prec'].index.get_level_values(1)).mean()
    desvio=dados['prec'].groupby(dados['prec'].index.get_level_values(1)).std()
    media_ET=dados['ETo'].groupby(dados['ETo'].index.get_level_values(1)).mean()
    desvio_ET=dados['ETo'].groupby(dados['ETo'].index.get_level_values(1)).std()
    q90=pd.DataFrame()
    for i in range(1000):
        #Para mudar a precipitação
        x=pd.DataFrame()
        for j in range(12):
            if (j==11)|(j==0)|(j==1):
                aleatorio=np.random.normal(loc=(media.iloc[j]*1.1439), scale=desvio.iloc[j], size=30)
                while aleatorio.min()<0:
                    aleatorio=np.random.normal(loc=(media.iloc[j]*1.1439), scale=desvio.iloc[j], size=30)
                x=pd.concat([x,pd.DataFrame({str(j+1):aleatorio})],axis=1)
            elif (j==2)|(j==3)|(j==4):
                aleatorio=np.random.normal(loc=(media.iloc[j]*0.918), scale=desvio.iloc[j], size=30)
                while aleatorio.min()<0:
                    aleatorio=np.random.normal(loc=(media.iloc[j]*0.918), scale=desvio.iloc[j], size=30)
                x=pd.concat([x,pd.DataFrame({str(j+1):aleatorio})],axis=1)
            elif (j==5)|(j==6)|(j==7):
                aleatorio=np.random.normal(loc=(media.iloc[j]*1.346), scale=desvio.iloc[j], size=30)
                while aleatorio.min()<0:
                    aleatorio=np.random.normal(loc=(media.iloc[j]*1.346), scale=desvio.iloc[j], size=30)
                x=pd.concat([x,pd.DataFrame({str(j+1):aleatorio})],axis=1)                
            elif (j==8)|(j==9)|(j==10):
                aleatorio=np.random.normal(loc=(media.iloc[j]*0.7772), scale=desvio.iloc[j], size=30)
                while aleatorio.min()<0:
                    aleatorio=np.random.normal(loc=(media.iloc[j]*0.7772), scale=desvio.iloc[j], size=30)
                x=pd.concat([x,pd.DataFrame({str(j+1):aleatorio})],axis=1)                                
        x=x.transpose()
        Prec1=[]
        for coluna in x:
            Prec1=Prec1+list(x[coluna])
        PrecFinal=list(dados['prec'])+Prec1
        
        #Para mudar a ET0
        y=pd.DataFrame()
        for j in range(12):
            if (j==11)|(j==0)|(j==1):
                aleatorio=np.random.normal(loc=(media_ET.iloc[j]*1.0353), scale=desvio_ET.iloc[j], size=30)
                while aleatorio.min()<0:
                    aleatorio=np.random.normal(loc=(media_ET.iloc[j]*1.0353), scale=desvio_ET.iloc[j], size=30)
                y=pd.concat([y,pd.DataFrame({str(j+1):aleatorio})],axis=1)
            elif (j==2)|(j==3)|(j==4):
                aleatorio=np.random.normal(loc=(media_ET.iloc[j]*1.0429), scale=desvio_ET.iloc[j], size=30)
                while aleatorio.min()<0:
                    aleatorio=np.random.normal(loc=(media_ET.iloc[j]*1.0429), scale=desvio_ET.iloc[j], size=30)
                y=pd.concat([y,pd.DataFrame({str(j+1):aleatorio})],axis=1)
            elif (j==5)|(j==6)|(j==7):
                aleatorio=np.random.normal(loc=(media_ET.iloc[j]*1.0468), scale=desvio_ET.iloc[j], size=30)
                while aleatorio.min()<0:
                    aleatorio=np.random.normal(loc=(media_ET.iloc[j]*1.0468), scale=desvio_ET.iloc[j], size=30)
                y=pd.concat([y,pd.DataFrame({str(j+1):aleatorio})],axis=1)                
            elif (j==8)|(j==9)|(j==10):
                aleatorio=np.random.normal(loc=(media_ET.iloc[j]*1.0545), scale=desvio_ET.iloc[j], size=30)
                while aleatorio.min()<0:
                    aleatorio=np.random.normal(loc=(media_ET.iloc[j]*1.0545), scale=desvio_ET.iloc[j], size=30)
                y=pd.concat([y,pd.DataFrame({str(j+1):aleatorio})],axis=1)
        ET1=[]
        for coluna in y:
            ET1=ET1+list(y[coluna])
        ETFinal=list(dados['ETo'])+ET1
                    
        calculado=pd.DataFrame(smap(INI,PRM,PrecFinal,ETFinal)['Vazao'])
        calculado.index=pd.date_range(start='01/01/1980',periods=792,freq='MS')
        previsao=calculado[432:].groupby(calculado[432:].index.month).quantile(0.1)
        q90=pd.concat([q90,previsao])
        print(i)
    return q90

q90=analise(INI,PRM,dados)