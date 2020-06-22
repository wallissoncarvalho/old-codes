import os
import xarray as xr 
import geopandas as gpd
from shapely.geometry import Point
import pandas as pd

def retorna_serie(var,shape_num):
    serie_mes=pd.DataFrame()
    for file in os.listdir('NETCDF'):
        if file[0:len(var)]==var:
            dados=xr.open_dataset('NETCDF//'+file)
            pixels_df,serie = pixels_shape(dados,'shapes\\reconcavo.shp',shape_num)
            serie_mensal=serie.groupby([lambda x: x.year, lambda x: x.month]).mean()
            serie_mes=pd.concat([serie_mes,serie_mensal])
    serie_mes=serie_mes[var].to_frame()
    return serie_mes

shape_dir = 'C:\\Users\\Wallisson\\OneDrive\\Publicações\\2019\\GEV\\inputs\\shapes\\EstadosBR_IBGE_LLWGS84.shp'
net_cdf='C:\\Users\\Wallisson\\prec_daily_UT_Brazil_v2.2_20100101_20151231.nc'
shape_num=0
dados=xr.open_dataset(net_cdf)

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
            #pixels=pixels[pixels.geometry.within(area.geometry[shape_num].buffer(0.25))]
            pixels=pixels[pixels.geometry.within(area.geometry[shape_num])]
            pixels['Latitude']=pixels.geometry.y
            pixels['Longitude']=pixels.geometry.x
            x,y=[],[]
            serie=pd.DataFrame()
            for pixel in pixels['geometry']:
                lat=pixel.y
                lon=pixel.x
                x.append(lon)
                y.append(lat)
                serie=pd.concat([serie,dados.sel(latitude=pixel.y,longitude=pixel.x).to_dataframe()])
                pixels_df=pd.DataFrame({'Latitude':y,'Longitude':x})
            pixels=gpd.GeoDataFrame(pixels_df,crs=crs,geometry=pixels.geometry)
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


def txt_to_ascii_netcdf(serie_pontos,var_name,path_save):
    count=0
    for a in range(len(serie_pontos)):
        name_arq=var_name+'_pixel_'+str(a)+'.txt'
        count=count+1
        name_arq='0000000'+str(count)+'.txt'
        df=serie_pontos[a]
        df.index=df['time']
        df=df[var_name].to_frame()   
        df=df.round(decimals=2)
        data = pd.to_datetime('1/1/1980')
        arq = open(os.path.join(os.path.join(os.getcwd(),path_save), name_arq), 'w')
        for i in df.index:
            i=df[var_name][i]
            arq.write('{:>6}{:>6}{:>6}{:>12}\n'.format(data.day, data.month, data.year, float('%.2f'%(i))))
            data += pd.DateOffset(days=1)
        arq.close()
        
      
        
        
        
        
        
        
        
        
        
        
        