import os
import xarray as xr 
import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
from scipy.stats import gennorm, norm, kstest
import numpy as np
import matplotlib.pyplot as plt

shape_dir = 'D:\\NETCDF\\shp\\estados_2010.shp'
net_cdf_dir='D:\\NETCDF'
shape_num=0


def pixels_shape(net_cdf_dir,shape_dir,shape_num,var):
    area=gpd.read_file(shape_dir)
    files=[]
    for file in os.listdir(net_cdf_dir):
        if file[0:len(var)]==var:
            files.append(file)
    dados=xr.open_dataset(net_cdf_dir + '\\' +files[0])   
    for coord_name in list(dados.coords._names):
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
        pixels=pixels[pixels.geometry.within(area.geometry[shape_num].buffer(.15))]
        pixels['Latitude']=pixels.geometry.y
        pixels['Longitude']=pixels.geometry.x
        series=pd.DataFrame()
        count=1
        for pixel in pixels['geometry']:           
            serie=pd.DataFrame()
            for file in files:               
                dados=xr.open_dataset(net_cdf_dir + '\\' +file)
                serie=pd.concat([serie,dados.sel(latitude=pixel.y,longitude=pixel.x).to_dataframe()])
            serie=serie[var]
            serie=serie.rename('Pixel 0'+str(count))
            series=pd.concat([series,serie],axis=1)
            count+=1
    return series,pixels


def spi(net_cdf_dir,shape_dir):
    series,pixels = pixels_shape(net_cdf_dir,shape_dir,1,'prec')
    pixels['Name']=list(series.columns)
    series_mensais = series.groupby(pd.Grouper(freq=('MS'))).sum()
    def calcula_eventos(acumulado):
        eventos_total=[]
        for name in acumulado.columns:
            mvs_parameters=gennorm.fit(acumulado[name])
            beta, loc, scale = mvs_parameters
            
            c, loc, scale = mvs_parameters
            mvs_test=kstest(acumulado[name],'gennorm', args=(mvs_parameters))
            statistic,pvalue=mvs_test
            acumulado[name]=acumulado[name].apply(lambda x:gennorm.cdf(x, beta, loc,scale))  
            acumulado[name]=acumulado[name].apply(lambda x:norm.ppf(x,loc=0,scale=1))
            eventos=0
            flag=0
            for i in range(len(acumulado[name].index)):
                if i==0:
                    if acumulado[name][i]<=-1:
                        eventos+=1
                else:
                    if acumulado[name][i]<=-1 and flag==0:
                        eventos+=1
                        flag=1
                    elif acumulado[name][i]>=0:
                        flag=0
            eventos_total.append(eventos)
        return eventos_total    
    pixels['SPI 12']=calcula_eventos(series_mensais.rolling(12).sum().dropna())
    pixels['SPI 6']=calcula_eventos(series_mensais.rolling(6).sum().dropna())
    pixels['SPI 3']=calcula_eventos(series_mensais.rolling(3).sum().dropna())
    pixels['SPI 1']=calcula_eventos(series_mensais)



    
def plot_fill(chuva,name):
    fig=plt.figure(num=None, figsize=(12, 2), dpi=80)
    ax=fig.add_subplot(1,1,1)   
    #DADOS
    x=chuva.index.to_frame()
    x=np.array(x['time'].apply(lambda x:(x.year)))
    y=np.array(chuva[name])
    
    #PINTAS DADOS POSITIVOS E NEGATIVOS
    plt.fill_between(x, 0, y, where=y>0, interpolate=True, color='blue')
    plt.fill_between(x, 0, y, where=y<0, interpolate=True, color='red')
    
    
    ax.grid(which='both',alpha=0.2)
    plt.show()

