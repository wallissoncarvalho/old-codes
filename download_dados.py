# -*- coding: utf-8 -*-
"""
#BAIXAR SELENIUM,
Adicionar geckodriver.exe nas variáveis do sistema, para isso fazer o download em https://github.com/mozilla/geckodriver/releases
Em seguida extrair a pasta em C:/Program Files, abrir "Configurações Avançadas do Sistema", Clicar em "Variáveis de Ambiente"
Em "váriaveis so sistema" clicar em "Path" e em seguida clicar em "Editar", na janela aberta clicar em "Novo"
Adicionar o caminho C:/Program Files/nome_da_pasta em que o geckodriver.exe está inserida
Reiciar o computador
"""

import time
import os
import zipfile
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import calendar
from plotly.offline import plot
import plotly.figure_factory as ff
import numpy as np
import matplotlib.pyplot as plt

def postos_na_area(inventario_hidroweb_dir,shape_area_dir,buffer=0):
    """Baseado em um arquivo no formato excel do inventário de estações que contém as informações de Latitude, Longitude e Código dos postos
       retorna as estações que estão presentes na área ou ao redor (buffer) do shapefile fornecido;
       Obs. As coordenadas das estações e o shapefile e devem estar com o sistema de coordenadas de referência WG84
    """ 
    #O SHAPE DEVE ESTAR NO SISTEMA DE REFERÊNCIA WGS-84
    shape_area=gpd.read_file(shape_area_dir)
    shape_area2=gpd.read_file(shape_area_dir)
    del shape_area2['geometry']
    if shape_area.shape[0]>1:
        print('Shapefile com mais de uma geometria...')
        print(shape_area2)
        shape_num=int(input('Selecione o index do shapefile desejado: '))
    else:
        shape_num=0
    postos_hidroweb=pd.read_excel(inventario_hidroweb_dir)
    postos_area=[Point(x) for x in zip(postos_hidroweb['Longitude'],postos_hidroweb['Latitude'])]
    crs={'proj':'latlong','ellps':'WGS84','datum':'WGS84','no_def':True} #SC WGS 8
    postos_area=gpd.GeoDataFrame(crs=crs,geometry=postos_area)            
    postos_area=postos_area[postos_area.geometry.within(shape_area.geometry[shape_num].buffer(buffer))]
    x,y=[],[]
    for coordenadas in postos_area['geometry']:
        lat=coordenadas.y
        lon=coordenadas.x
        x.append(lon)
        y.append(lat)
    postos_area={'Latitude':y,'Longitude':x}
    postos_area=pd.DataFrame(data=postos_area)
    postos_area=postos_hidroweb.merge(postos_area,on=['Latitude','Longitude'])
    postos_area=postos_area.drop_duplicates(subset='Codigo')
    return postos_area

def download_hidroweb(id_stations,dir_trab):
    """ Baseado em uma lista de código das estações, a função faz o download automático e salva no diretório fornecido (dir_trab)
    """
    dir_out=dir_trab+'\\DADOS_HIDROWEB\\BAIXADOS'
    if not os.path.exists(dir_out):
        os.makedirs(dir_out)
    #CONFIGURAÇÃO FIREFOX WEBDRIVER
    options = Options();
    options.headless = True #TORNA O NAVEGADOR INVISÍVEL
    options.set_preference("browser.download.folderList",2);
    options.set_preference("browser.download.manager.showWhenStarting", False);
    options.set_preference("browser.download.dir",dir_out);
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/octet-stream,application/vnd.ms-excel");
    browser = webdriver.Firefox(options=options);
    #INICIA WEBDRIVER
    url = 'http://www.snirh.gov.br/hidroweb/publico/apresentacao.jsf'
    browser.get(url) 
    time.sleep(1)
    #DEFINE A FUNÇÃO PARA CLICKS
    def try_click(element):
        count=0
        while count!=20:
            try:
                element.click()
                count=20
            except:
                time.sleep(1)
                count+=1
            if count==19:
                print('Tempo de espera excedido. Processo encerrado')
                exit()
    nao_baixados=[]    
    for i in range(len(id_stations)):
        id_station=str(id_stations[i])
        print('Baixando a estação {}, código {}'.format(i+1,id_station))
        time.sleep(1)
        try:
            _ = WebDriverWait(browser, 15).until(EC.presence_of_element_located((By.LINK_TEXT, 'Séries Históricas')))
            browser.find_element_by_link_text('Séries Históricas').click()
        except:
            nao_baixados.append(id_station)
            print('Tempo de espera excedido. Processo encerrado')
            continue
        try:
            _ = WebDriverWait(browser, 15).until(EC.presence_of_element_located((By.ID,'form:fsListaEstacoes:codigoEstacao')))
            browser.find_element_by_id('form:fsListaEstacoes:codigoEstacao').send_keys([id_station, Keys.ENTER])
        except:
            nao_baixados.append(id_station)
            print('Tempo de espera excedido. Processo encerrado')
            continue
        try:
            _ = WebDriverWait(browser, 15).until(EC.presence_of_element_located((By.LINK_TEXT, 'Consultar')))
            time.sleep(1)
            browser.find_element_by_link_text('Consultar').click()  
        except:
            nao_baixados.append(id_station)
            print('Tempo de espera excedido. Processo encerrado')
            continue
        
        try:
            _ = WebDriverWait(browser,15).until(EC.presence_of_element_located((By.ID,'form:fsListaEstacoes:fsListaEstacoesC:j_idt178:table:0:ckbSelecionada')))
            time.sleep(1)
            try_click(browser.find_element_by_name('form:fsListaEstacoes:fsListaEstacoesC:j_idt178:table:0:ckbSelecionada'))
        except:
            print('Nenhum registro encontrado.')
            continue
        
        try:
            _ = WebDriverWait(browser,15).until(EC.presence_of_element_located((By.CSS_SELECTOR,'#form\\:fsListaEstacoes\\:fsListaEstacoesC\\:radTipoArquivo-componente > div:nth-child(2) > div:nth-child(3)')))
            time.sleep(1)
            try_click(browser.find_element_by_css_selector('#form\\:fsListaEstacoes\\:fsListaEstacoesC\\:radTipoArquivo-componente > div:nth-child(2) > div:nth-child(3)'))
        except:
            nao_baixados.append(id_station)
            print('Tempo de espera excedido. Processo encerrado')
            continue
        
        try:
            _ = WebDriverWait(browser,15).until(EC.presence_of_element_located((By.CSS_SELECTOR,'#form\\:fsListaEstacoes\\:fsListaEstacoesC\\:btBaixar')))
            time.sleep(1)
            try_click(browser.find_element_by_css_selector('#form\\:fsListaEstacoes\\:fsListaEstacoesC\\:btBaixar'))
        except:
            nao_baixados.append(id_station)
            print('Tempo de espera excedido. Processo encerrado')
            continue
    time.sleep(2)

    browser.close()
    time.sleep(3)
    #RECURSÃO PARA O CASO DE ALGUMA ESTAÇÃO NÃO TER SIDO BAIXADA POR INSTABILIDADE DO SISTEMA
    if len(nao_baixados)==0:
        print('Todas as estações foram baixadas')
    else:
        print('As estações a seguir ainda não foram baixadas, por instabilidade na navegação: ')
        print(nao_baixados)
        stations_rest=nao_baixados
        salvar = pd.DataFrame(nao_baixados)
        salvar.to_csv(dir_trab+'\\nao_baixados.csv')
        print('Baixando estações que ainda não foram baixadas...')
        download_hidroweb(stations_rest,dir_trab)

def descompactar(dir_baixados,var):
    '''Descompacta a variável de interesse 'var' das estações no formato .zip baixados do Hidroweb (deve ser baixado no formato .csv)
       e salva no diretório fornecido
    '''  
    for root,dirs,files in os.walk(dir_baixados):
        for name in files:
            if name[-3:] =='zip':
                zip_ref=zipfile.ZipFile(dir_baixados + name,'r')
                zip_ref.extractall(dir_baixados + '\\EXTRACT')
                zip_ref.close()            
    for root,dirs,files in os.walk(dir_baixados + '\\EXTRACT'):
        for name in files:
            if name[0:len(var)]==var:
                zip_ref=zipfile.ZipFile(dir_baixados + '\\EXTRACT\\'+name,'r')
                zip_ref.extractall(dir_baixados + '\\EXTRAIDOS')
                zip_ref.close()
    shutil.rmtree(dir_trab + '\\DADOS_HIDROWEB\\EXTRACT') 
    
def converte_dados(dir_dados): 
    """Converte os dados do hidroweb para um dataframe onde cada coluna refere-se à uma estação;
       dir_dados -> Diretório no computador onde estão os dados das estações no formato .csv;
       PARA MELHOR SEPARAR O DATAFRAME DEIXAR OS ARQUIVOS DE APENAS UMA VARIÁVEL EM dir_dados
    """     
    dados=pd.DataFrame()
    count=1
    for root,dirs,files in os.walk(dir_dados):
        for file in files:
            if file[-3:] == 'csv':
                if file[:6]=='vazoes':
                    skiprows,coluna_inicio,coluna_fim=14,16,15
                elif file[:6]=='chuvas':
                    skiprows,coluna_inicio,coluna_fim=13,13,12
                elif file[:5]=='cotas':
                    skiprows,coluna_inicio,coluna_fim=14,16,15
                df=pd.read_csv(dir_dados+'\\'+file,sep=';',skiprows=skiprows,header=None)
                #df[2]=df[2].apply(lambda x:str(x))
                df[2]=df[2].apply(lambda x:'01'+x[2:])
                df[2] =  pd.to_datetime(df[2], format='%d/%m/%Y')
                df=df.loc[df.groupby(2)[1].idxmax()] #REMOVE OS DADOS DUPLICADOS QUE COM CONSISTÊNCIA 1
                df.index=df[2]
                #TRANSFORMA OS DADOS PARA SÉRIE CONTÍNUA COM UMA COLUNA:
                lista_series_mensais=[]
                for data in list(df[2]):
                    ultimo_dia=calendar.monthrange(data.year,data.month)[1]
                    mes=pd.date_range(data,periods=ultimo_dia, freq='D')
                    serie_linha=pd.Series(df.loc[data,coluna_inicio:coluna_fim+ultimo_dia], name='Dados')
                    serie = pd.Series(list(serie_linha),index = mes)
                    lista_series_mensais.append(serie)
                serie_completa=pd.concat(lista_series_mensais)
                serie_completa=serie_completa.apply(lambda x: float(x.replace(',','.')) if isinstance(x,str) else x)
                serie_completa=serie_completa.sort_index()
                data_index = pd.date_range(serie_completa.index[0], serie_completa.index[-1], freq='D')
                serie_completa=serie_completa.reindex(data_index)
                serie_completa.sort_index()
                serie_completa=serie_completa.to_frame()
                serie_completa=serie_completa.rename(columns={0:file[-12:-4]})
                print('Estação {}: {}'.format(count,file[-12:-4]))
                count+=1
                dados=pd.concat([dados,serie_completa],axis=1)        
    dados.dropna(axis=1,how='all',inplace=True)
    data_index = pd.date_range(dados.index[0], dados.index[-1], freq='D')
    dados=dados.reindex(data_index)  
    return dados

def numero_estacoes(dados):
    ''' Retorna o gráfico do número de estações com dados para cada ano contido no DataFrame dados;
        O gráfico contabiliza uma estação num determinado ano de dados aquelas que tem até 5%, 10% ou 15% de falhas.
    '''
    years=list(set(dados.index.year))
    lista_5 = []
    lista_10 = []
    lista_15 = []
    for year in years:
        series = dados.loc[dados.index.year==year]
        falhas=series.isnull().sum().to_frame()
        est_dados5 = list(falhas.loc[falhas[falhas.columns[0]]<19].index)
        lista_5.append(len(est_dados5))
        est_dados10 = list(falhas.loc[falhas[falhas.columns[0]]<37].index)
        lista_10.append(len(est_dados10))
        est_dados15 = list(falhas.loc[falhas[falhas.columns[0]]<55].index)
        lista_15.append(len(est_dados15))
    corte = 0
    while lista_5[corte] == 0 and lista_10[corte] == 0 and lista_15[corte] == 0:
        corte +=1
    years = years[corte:-1]
    lista_5 = lista_5[corte:-1]
    lista_10 = lista_10[corte:-1]
    lista_15 = lista_15[corte:-1]
    
    _ = plt.bar(years,lista_15,.9)
    _ = plt.bar(years,lista_10,.9)
    _ = plt.bar(years,lista_5,.9)
    plt.ylabel('Number of stations')
    plt.xlabel('Years')
    plt.xticks(np.arange(min(years),max(years),5))
    plt.yticks(np.arange(0,max(lista_15)+1,50))
    plt.legend(('5%','10%','15%'))
    plt.show()
