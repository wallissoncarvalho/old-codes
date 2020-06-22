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
#from selenium import webdriver
#from selenium.webdriver.common.by import By
#from selenium.webdriver.support.wait import WebDriverWait
#from selenium.webdriver.support import expected_conditions as EC
#from selenium.webdriver.common.keys import Keys
#from selenium.webdriver.firefox.options import Options
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

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

def hidroweb(id_stations,dir_trab):
    """ Baseado em uma lista de código das estações, a função faz o download automático e salva no diretório fornecido (dir_trab)
    """
    dir_out=dir_trab+'\\BAIXADOS'
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
            print('Tempo de espera excedido. Baixando a próxima estação.')
            continue
        try:
            _ = WebDriverWait(browser, 15).until(EC.presence_of_element_located((By.ID,'form:fsListaEstacoes:codigoEstacao')))
            browser.find_element_by_id('form:fsListaEstacoes:codigoEstacao').send_keys([id_station, Keys.ENTER])
        except:
            nao_baixados.append(id_station)
            print('Tempo de espera excedido. Baixando a próxima estação.')
            continue
        try:
            _ = WebDriverWait(browser, 15).until(EC.presence_of_element_located((By.LINK_TEXT, 'Consultar')))
            time.sleep(1)
            browser.find_element_by_link_text('Consultar').click()
        except:
            nao_baixados.append(id_station)
            print('Tempo de espera excedido. Baixando a próxima estação.')
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
            print('Tempo de espera excedido. Baixando a próxima estação.')
            continue

        try:
            _ = WebDriverWait(browser,15).until(EC.presence_of_element_located((By.CSS_SELECTOR,'#form\\:fsListaEstacoes\\:fsListaEstacoesC\\:btBaixar')))
            time.sleep(1)
            try_click(browser.find_element_by_css_selector('#form\\:fsListaEstacoes\\:fsListaEstacoesC\\:btBaixar'))
        except:
            nao_baixados.append(id_station)
            print('Tempo de espera excedido. Baixando a próxima estação.')
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
        print('Baixando estações que ainda não foram baixadas...')
        hidroweb(stations_rest,dir_trab)

def descompactar(dir_baixados,var):
    '''Descompacta a variável de interesse 'var' das estações no formato .zip baixados do Hidroweb (deve ser baixado no formato .csv)
       e salva no diretório fornecido
    '''
    for root,dirs,files in os.walk(dir_baixados):
        for name in files:
            if name[-3:] =='zip':
                zip_ref=zipfile.ZipFile(dir_baixados +'\\'+ name,'r')
                zip_ref.extractall(dir_baixados + '\\EXTRACT')
                zip_ref.close()
    for root,dirs,files in os.walk(dir_baixados + '\\EXTRACT'):
        for name in files:
            if name[0:len(var)]==var:
                zip_ref=zipfile.ZipFile(dir_baixados + '\\EXTRACT\\'+name,'r')
                zip_ref.extractall(dir_baixados + '\\EXTRAIDOS\\')
                zip_ref.close()
    shutil.rmtree(dir_baixados + '\\EXTRACT')
