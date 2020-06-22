#IMPORTANDO AS FUNÇÕES
import baixar
import metodos
import plotar
import converter
import pandas as pd
import geopandas as gpd


#DECLARAÇÕES DE DIRETÓRIOS DE TRABALHO E DADOS DE ENTRADA DAS FUNÇÕES

#UFAL
dir_loc = 'D:\\Data\\Mundau'
#CASA
#dir_loc = 'D:\\OneDrive\\'

inventario_hidroweb_dir = 'D:\\OneDrive\\Sao_Francisco\\inputs\\inventario_hidroweb.xls'
shape_area_dir = dir_loc + '\\Mundau_Watershed.shp'
dir_trab=dir_loc + 'Sao_Francisco\\PLU'
dir_dados=dir_loc + 'Sao_Francisco\\PLU\\TODAS'
dir_dados_pkl = dir_loc + 'Sao_Francisco\\PLU\\PKL'
#
#      
postos_area=baixar.postos_na_area(inventario_hidroweb_dir,shape_area_dir,buffer=0)
postos_area_plu = postos_area[postos_area['TipoEstacao'] == 2]
#postos_area_flu_s = postos_area_flu[postos_area_flu['Codigo'].isin([39870000,39850000,39860000])]



'''
Dia 08/08/2019
dados=converter.hidroweb(dir_dados)
dados=metodos.filtrar_estacoes(dados,janela_inicio='01/01/1940',janela_fim='31/12/2018')
dados.to_pickle(dir_dados_pkl+'\\TODAS_POS_FILTROS.pkl') #SALVA O DATAFRAME EM UM ARQUIVO PICKLE MAIS RÁPIDO DE CARREGAR. PARA CARREGAR USAR pd.read_pickle

#FORAM GERADOS OS SHAPES COM AS ESTAÇÕES CONTIDAS NAS TRÊS REGIÕES DE INTERESSES: EXEMPLO ABAIXO REGIÃO B
shape_postos_area=metodos.shape_estacoes_area(dados,inventario_hidroweb_dir,shape_area_dir)
shape_postos_area.to_file(dir_loc + 'Sao_Francisco\\SIG\\shp\\BH\PZ\\Estacoes_RB_WGS84.shp')

#CONFERIR O GANTT GERADO PÓS-FILTRO
plotar.gantt(dados,'TODAS-POS-FILTRO')
'''

'''
Dia 13/08/2019

#RB
estacoes_rb = gpd.read_file(dir_loc + 'Sao_Francisco\\SIG\\shp\\BH\PZ\\Estacoes_RB_WGS84.shp')
shape_estacoes_rb,codigos_rb = metodos.distance_central_point(estacoes_rb,n=90)
shape_estacoes_rb.to_file(dir_loc + 'Sao_Francisco\\SIG\\shp\\BH\PZ\\Estacoes_RB_WGS84.shp')
dados_rb=dados[codigos_rb]
dados_rb.to_pickle(dir_dados_pkl+'\\RB_90_PROXIMAS.pkl')
plotar.gantt(dados_rb,'RB_90_PROXIMAS')
dados_rb=dados_rb.fillna('NA')
dados_rb.to_csv(dir_trab + '\\RB_90_PROXIMAS.csv')


#RA
estacoes_ra = gpd.read_file(dir_loc + 'Sao_Francisco\\SIG\\shp\\BH\PZ\\Estacoes_RA_WGS84.shp')
shape_estacoes_ra,codigos_ra = metodos.distance_central_point(estacoes_ra,n=90)
shape_estacoes_ra.to_file(dir_loc + 'Sao_Francisco\\SIG\\shp\\BH\PZ\\Estacoes_RA_WGS84.shp')
dados_ra=dados[codigos_ra]
dados_ra.to_pickle(dir_dados_pkl+'\\RA_90_PROXIMAS.pkl')
plotar.gantt(dados_ra,'RA_90_PROXIMAS')
dados_ra=dados_ra.fillna('NA')
dados_ra.to_csv(dir_trab + '\\RA_90_PROXIMAS.csv')


#RT
estacoes_rt = gpd.read_file(dir_loc + 'Sao_Francisco\\SIG\\shp\\BH\PZ\\Estacoes_RT_WGS84.shp')
shape_estacoes_rt,codigos_rt = metodos.distance_central_point(estacoes_rt,n=90)
shape_estacoes_rt.to_file(dir_loc + 'Sao_Francisco\\SIG\\shp\\BH\PZ\\Estacoes_RT_WGS84.shp')
dados_rt=dados[codigos_rt]
dados_rt.to_pickle(dir_dados_pkl+'\\RT_90_PROXIMAS.pkl')
plotar.gantt(dados_rt,'RT_90_PROXIMAS')
dados_rt=dados_rt.fillna('NA')
dados_rt.to_csv(dir_trab + '\\RT_90_PROXIMAS.csv')



Dia 25/09/2019

#RB
dados_rb = pd.read_pickle(dir_dados_pkl+'\\RB_90_PROXIMAS.pkl')
dados_mensais_rb = metodos.agrupa_mensal(dados_rb)
dados_mensais_rb.to_pickle(dir_dados_pkl+'\\RB_90_PROXIMAS_MENSAIS.pkl')
dados_mensais_rb=dados_mensais_rb.fillna('NA')
dados_mensais_rb.to_csv(dir_trab + '\\RB_90_PROXIMAS_MENSAIS.csv')



'''





#shape_postos_area=metodos.shape_estacoes_area(dados,inventario_hidroweb_dir,shape_area_dir)
#shape_postos_area.to_file(dir_loc + 'Sao_Francisco\\SIG\\shp\\BH\PZ\\Estacoes_RT_WGS84.shp')
#postos_area=baixar.postos_na_area(inventario_hidroweb_dir,shape_area_dir,buffer=0)
#postos_area=postos_area[postos_area['TipoEstacao']==2]




#plotar.numero_estacoes_ano(dados)
#postos_com_dados=plotar.gantt(dados,'RB')
#postos_area=postos_na_area(inventario_hidroweb_dir,shape_area_dir,buffer=0)
#postos_area=postos_area[postos_area['TipoEstacao']==2]
#id_stations=list(postos_area['Codigo'])
##download_hidroweb(id_stations,dir_trab)
#dados=converte_dados(dir_dados)
#postos_com_dados=postos_area.merge(postos_com_dados,on=['Codigo'])
#plot_estacoes_area(postos_com_dados,shape_area_dir)