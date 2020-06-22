import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta
from shapely.geometry import Point

def filtrar_estacoes(dados,n_anos=10,percent_falhas=5,janela_inicio=False,janela_fim=False):
    '''Seleciona as estações que tem pelo menos n_anos de dados entre a primeira e a última medição registrada;
       As estações selecionadas serão filtradas para um máximo de percent_falhas (0% a 100%) em um período de n_anos;
       Pode ser definida uma janela de tempo com as datas janela_inicio e janela_fim para recortar o DataFrame dados;
    '''
    #RECORTE JANELA: Caso sejam passadas datas de interesse para os dados, serão recortadas as janelas de interesse.
    if janela_inicio!=False and janela_fim!=False:
        janela_inicio=pd.to_datetime([janela_inicio])
        janela_fim=pd.to_datetime([janela_fim])
        dados=dados.loc[janela_inicio[0]:janela_fim[0]]        
    elif janela_inicio!=False:
        janela_inicio=pd.to_datetime([janela_inicio])
        dados=dados.loc[janela_inicio[0]:]
    elif janela_fim!=False:
        janela_fim=pd.to_datetime([janela_fim])
        dados=dados.loc[:janela_fim[0]]
    
    #FILTRO 1: Seleciona estações que tenham pelo menos n_anos de registro de dados.
    estations = []
    for column in dados.columns:
        serie = dados[column]
        serie_drop = serie.dropna()
        if len(serie_drop)>0:
            anos = (serie_drop.index[-1]-serie_drop.index[0])/np.timedelta64(1,'Y')
            if anos>=n_anos:
                estations.append(column)
    dados=dados[estations]
    
    #FILTRO 2: Verifica se há pelo menos uma janela com 10 anos de registro com até no máximo percent_falhas.
    estations=[]
    state = 0
    for column in dados.columns:
        print('Decorreu {}%'.format(round(state/len(dados.columns)*100,1)))
        serie = dados[column]
        serie_drop = serie.dropna()    
        periodos = []
        Start1 = serie_drop.index[0]
        Finish1 = 0
        for i in range(len(serie_drop)):
            if i!=0 and (serie_drop.index[i]-serie_drop.index[i-1])/np.timedelta64(1,'D') != 1:
                Finish1=serie_drop.index[i-1]
                periodos.append(dict(Start=Start1,Finish=Finish1,Intervalo=(Finish1-Start1)/np.timedelta64(1,'Y')))
                Start1 = serie_drop.index[i]
                Finish1 = 0
        Finish1 = serie_drop.index[-1]
        periodos.append(dict(Start=Start1,Finish=Finish1,Intervalo=(Finish1-Start1)/np.timedelta64(1,'Y')))
        periodos=pd.DataFrame(periodos)
        if len(periodos[periodos['Intervalo']>=n_anos])>0:
             estations.append(column)
        else:
            j=0
            aux=0
            while j<len(periodos) and aux==0:
                j+=1
                if periodos['Start'][j] + relativedelta(years=n_anos) <= periodos['Finish'][periodos.index[-1]]:
                    serie_periodo=serie.loc[periodos['Start'][j]:periodos['Start'][j] + relativedelta(years=n_anos)]
                    falhas=serie_periodo.isnull().sum()/len(serie_periodo)
                    if falhas<=percent_falhas/100 and aux==0:
                        aux=1
                        estations.append(column)
                else:
                    aux=1
        state+=1
    dados=dados[estations]
    return dados

def shape_estacoes_area(dados,inventario_hidroweb_dir,shape_area_dir,buffer=0):
    ''' Retorna o shapefile da estações contidas no dataframe dados e que estão presentes em uma área de interesse.            
    '''   
    import baixar
    from shapely.geometry import Point
    import geopandas as gpd
    postos_area=baixar.postos_na_area(inventario_hidroweb_dir,shape_area_dir,buffer=0)
    postos_dados=[] 
    for column in dados.columns:
        postos_dados.append(int(column))
    postos_dados={'Codigo':postos_dados}
    postos_dados=pd.DataFrame(data=postos_dados)
    postos_dados=postos_area.merge(postos_dados,on=['Codigo'])
    shape_postos_area=[Point(x) for x in zip(postos_dados['Longitude'],postos_dados['Latitude'])]
    crs={'proj':'latlong','ellps':'WGS84','datum':'WGS84','no_def':True} #SC WGS 8
    shape_postos_area=gpd.GeoDataFrame(crs=crs,geometry=shape_postos_area)
    shape_postos_area['Codigo']=postos_dados['Codigo']
    shape_postos_area['Latitude']=postos_dados['Latitude']
    shape_postos_area['Longitude']=postos_dados['Longitude']
    return shape_postos_area


def distance_central_point(shape_estacoes,n=60):
    ''' Retorna o shapefile com o atributo Distances, onde é calculada a distância entre cada Estação e a coordenada central das estações
        Retorna as n estações mais próximas do ponto central
    '''
    center_point=Point(shape_estacoes['Longitude'].mean(),shape_estacoes['Latitude'].mean())
    distances = []
    distances=[center_point.distance(x) for x in shape_estacoes['geometry']]
    shape_estacoes['Distances']=distances
    codigos=list(shape_estacoes.sort_values('Distances')['Codigo'][0:n])    
    codigos = ['{:0>8}'.format(i) for i in codigos]
    return shape_estacoes,codigos
    
    
def agrupa_mensal(dados):
    dados_mensais = pd.DataFrame()
    for column in dados.columns:
        serie = dados[column]
        serie_mensal = serie.groupby(pd.Grouper(freq='1MS')).sum().to_frame()
        falhas=serie.isnull().groupby(pd.Grouper(freq='1MS')).sum().to_frame()
        to_drop=falhas.loc[falhas[column] > 0] #UM MÊS COM AUSÊNCIA DE 1 DADO É CONSIDERADO COM FALHA
        serie_mensal = serie_mensal.drop(index=to_drop.index).sort_index()
        data_index = pd.date_range(serie_mensal.index[0], serie_mensal.index[-1], freq='MS')
        serie_mensal=serie_mensal.reindex(data_index)
        dados_mensais = pd.concat([dados_mensais,serie_mensal],axis=1)
    return dados_mensais

def shape_postos(postos_dados):
    from shapely.geometry import Point
    import geopandas as gpd
    shape_postos=[Point(x) for x in zip(postos_dados['Longitude'],postos_dados['Latitude'])]
    crs={'proj':'latlong','ellps':'WGS84','datum':'WGS84','no_def':True} #SC WGS 8
    shape_postos=gpd.GeoDataFrame(crs=crs,geometry=shape_postos)
    shape_postos.index = postos_dados.index
    shape_postos['Code']=postos_dados['Codigo']
    shape_postos['Lat']=postos_dados['Latitude']
    shape_postos['Long']=postos_dados['Longitude']
    shape_postos['Drain_Area(Km2)'] = postos_dados['AreaDrenagem']
    return shape_postos
    
    
    
    
    