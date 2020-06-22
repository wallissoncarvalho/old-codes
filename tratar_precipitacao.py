# -*- coding: utf-8 -*-
import pandas as pd
import calendar
from plotly.offline import plot
import plotly.figure_factory as ff

from download_dados import converte_dados, gantt_plot,plot_estacoes_area,postos_na_area

def filtrar_anos(dados,anos):
    lista=[]
    for coluna in dados.columns:
        indice=dados[coluna].dropna().index
        if indice[-1].year-indice[0].year>=anos:
            lista.append(coluna)
    return dados[lista]

def dados_info(dados,freq):
    inicio,fim,estacoes,falhas,anos=[],[],[],[],[]
    dados.dropna(how='all',axis=1,inplace=True)
    for colum in dados.columns:
        dado=dados[colum].dropna()
        data_index = pd.date_range(dado.index[0], dado.index[-1], freq=freq)
        dado=dado.reindex(data_index)
        #estacoes.append(int(colum))
        estacoes.append(colum)
        inicio.append(str(dado.index[0].month)+'/'+str(dado.index[0].year))
        fim.append(str(dado.index[-1].month)+'/'+str(dado.index[-1].year))
        anos.append((dado.index.year[-1]-dado.index.year[0]+abs(dado.index.month[-1]-dado.index.month[0])/12).round(2))
        falhas.append((1-len(dado.dropna())/len(dado))*100)
    info=pd.DataFrame({'Codigo':estacoes,'Inicio':inicio,'Fim':fim,'Anos':anos,'Falhas(%)':falhas})
    return info
    
def filtro_mensal(dados):
    falhas_mensais=dados.isnull().groupby(pd.Grouper(freq='M')).sum()
    acumulado_mensal=dados.groupby(pd.Grouper(freq='M')).sum()
    dados_mes=pd.DataFrame()
    for coluna in dados.columns:
    #REMOVER MESES COM FALHA
        falha_coluna=falhas_mensais[coluna].to_frame()
        acumulado_coluna=acumulado_mensal[coluna].to_frame()
        falha_periodo=falha_coluna.loc[falha_coluna[coluna] > 0]
        acumulado_coluna=acumulado_coluna.drop(index=falha_periodo.index).sort_index()
        dados_mes=pd.concat([dados_mes,acumulado_coluna],axis=1)
    return dados_mes

def filtro_falhas(dados,freq,falhas):
    info=dados_info(dados,freq)
    info=info.loc[info['Falhas(%)']<falhas]
    dados=dados[list(info['Codigo'])]
    return dados



    