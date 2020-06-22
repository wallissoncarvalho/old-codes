import geopandas as gpd
from shapely.geometry import Point
import matplotlib as plt


def plot_estacoes_area(postos_com_dados,shape_area_dir,label=True):
    ''' Retorna o mapa das estações contidas no shapefile posto_com_dados, sobre a área de interesse;
        O shapefile deve ter como atributo os pontos com 'Longitude', 'Latitude' e 'Codigo'
    '''
    shape_area=gpd.read_file(shape_area_dir)
    shape_postos_area = []  
    shape_postos_area=[Point(x) for x in zip(postos_com_dados['Longitude'],postos_com_dados['Latitude'])]
    crs={'proj':'latlong','ellps':'WGS84','datum':'WGS84','no_def':True} #SC WGS 8
    shape_postos_area=gpd.GeoDataFrame(crs=crs,geometry=shape_postos_area)
    shape_postos_area['Codigo']=postos_com_dados['Codigo']
    base= shape_area.plot(color="white", edgecolor="black",figsize=(25,16),alpha=0.2)
    shape_postos_area.plot(ax=base,color="black",markersize=3)
    if label==True:
        for x, y, label in zip(shape_postos_area.geometry.x, shape_postos_area.geometry.y, shape_postos_area.Codigo):
            ax.annotate(label, xy=(x, y), xytext=(3, 3), textcoords="offset pixels")
    return shape_postos_area

        
