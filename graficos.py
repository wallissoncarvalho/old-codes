import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from math import ceil, log


def curva_permanencia(dados,logscale=True):
    plt.figure(num=None, figsize=(12, 9), dpi=100, facecolor='w', edgecolor='k')
    plt.grid(True,which="both",ls="-")
    ymax=0
    #ax = plt.gca()
    for name in dados.columns:
        serie=dados[name].dropna()
        n=len(serie)
        y = np.sort(serie)
        y = y[::-1]
        if ymax < y.max():
            ymax=y.max()
        x = (np.arange(1,n+1) / n)*100
        _ = plt.plot(x,y,linestyle='-') 
    plt.legend(list(dados.columns), loc='best')
    plt.margins(0.02) 
    if logscale==True:
        ticks = 10**np.arange(1,ceil(log(ymax,10)) + 1,1)
        ticks[-1:]+=1
        plt.yticks(list(ticks))
        plt.yscale('log')
        plt.tick_params(axis='y', which='minor')
        
    _ = plt.xlabel('Probabilidade de excedência ou igualdade (%)',fontsize=14)
    _ =  plt.ylabel('Vazão L/s',fontsize=14)
    plt.xticks(np.arange(0,101,step=10))
    plt.show()
    

def boxplot_mensal(dados):
    falhas_mensais=dados.isnull().groupby(pd.Grouper(freq='M')).sum()
    acumulado_mensal=dados.groupby(pd.Grouper(freq='M')).sum()
    for coluna in dados.columns:
        #REMOVER MESES COM 15% DE FALHA
        falha_coluna=falhas_mensais[coluna].to_frame()
        acumulado_coluna=acumulado_mensal[coluna].to_frame()
        falha_periodo=falha_coluna.loc[falha_coluna[coluna] > 4]
        acumulado_coluna=acumulado_coluna.drop(index=falha_periodo.index).sort_index()
        serie_por_mes=acumulado_coluna.groupby(by=acumulado_coluna.index.month)
        meses={}
        for group in serie_por_mes.groups:
            meses[group]=list(serie_por_mes.get_group(group)[coluna])
        meses=pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in meses.items() ]))
        ax=meses.boxplot(figsize=(15,10))
        ax.set_yticks(np.arange(0,701,step=100))
        ax.set_xlabel("Mês do Ano")
        ax.set_ylabel("Acumulado Mensal (mm/mês)")
        
        
def boxplot_mes(dados,nrows,ncolumns,figsize):
    falhas_mensais=dados.isnull().groupby(pd.Grouper(freq='M')).sum()
    acumulado_mensal=dados.groupby(pd.Grouper(freq='M')).sum()
    fig1, axs = plt.subplots(nrows, ncolumns, figsize=figsize, constrained_layout=True, sharey='all')
    def trim_axs(axs, N):
        axs = axs.flat
        for ax in axs[N:]:
            ax.remove()
        return axs[:N]
    axs = trim_axs(axs, len(dados.columns))
    for ax, coluna in zip(axs,dados.columns):
        #REMOVER MESES COM 15% DE FALHA
        falha_coluna=falhas_mensais[coluna].to_frame()
        acumulado_coluna=acumulado_mensal[coluna].to_frame()
        falha_periodo=falha_coluna.loc[falha_coluna[coluna] > 4]
        acumulado_coluna=acumulado_coluna.drop(index=falha_periodo.index).sort_index()
        serie_por_mes=acumulado_coluna.groupby(by=acumulado_coluna.index.month)
        meses=[]
        for group in serie_por_mes.groups:
            meses.append(list(serie_por_mes.get_group(group)[coluna]))
        ax.boxplot(meses)
        ax.set_title('Estação '+coluna)
        ax.set_xlabel("Mês do Ano")
        ax.set_ylabel("Acumulado Mensal (mm/mês)")
    

def prec_mensal(dados,nrows,ncolumns,figsize):
    falhas_mensais=dados.isnull().groupby(pd.Grouper(freq='M')).sum()
    acumulado_mensal=dados.groupby(pd.Grouper(freq='M')).sum()
    fig1, axs = plt.subplots(nrows, ncolumns, figsize=figsize, constrained_layout=True, sharey='all')
    def trim_axs(axs, N):
        axs = axs.flat
        for ax in axs[N:]:
            ax.remove()
        return axs[:N]
    axs = trim_axs(axs, len(dados.columns))
    for ax, coluna in zip(axs,dados.columns):
        #REMOVER MESES COM 15% DE FALHA
        falha_coluna=falhas_mensais[coluna].to_frame()
        acumulado_coluna=acumulado_mensal[coluna].to_frame()
        falha_periodo=falha_coluna.loc[falha_coluna[coluna] > 4]
        acumulado_coluna=acumulado_coluna.drop(index=falha_periodo.index).sort_index()
        serie_por_mes=acumulado_coluna.groupby(by=acumulado_coluna.index.month).mean()
        media=serie_por_mes[coluna].mean()
        xmin=list(serie_por_mes.index)[0]
        xmax=list(serie_por_mes.index)[-1]
        ax.bar(serie_por_mes.index,serie_por_mes[coluna],align='center')
        ax.hlines(y=media,xmin=xmin,xmax=xmax,linewidth=2,color='r',linestyle='dashed')
        ax.legend(('Média','Média Mensal'), loc='upper right')
        ax.set_title('Estação '+coluna,fontsize=14)
        ax.set_xlabel('Mês do ano',fontsize=14)
        ax.set_xticks(np.arange(1,12.1,step=1))
        ax.set_yticks(np.arange(0,400,step=50))
        ax.set_ylabel('Precipitação (mm/mês)',fontsize=14)
        
        
