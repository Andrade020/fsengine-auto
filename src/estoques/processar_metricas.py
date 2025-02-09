#     Bibliotecas de terceiros- third party   ###########################
#################  SPECIFIC    #########################################
from fuzzywuzzy import fuzz
from pandas.tseries.offsets import BDay
#################  STANDARD   ############################################
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
###################   buit-in  #########################################################
#from glob 
import glob
from datetime import datetime
import os
################################    ||  ############################# 
################### modulos locais  \/  #############################
class ProcessarMetricas:
    def __init__(self, df, data_referencia=None, feriados=None): # eh importante colcoar refdate pra ele nao usar a atual
        """
        inicializa a classe com o dataframe forncd, aplica otimizacoes e define a data de referencia.
      
        Melhora em relação ao RIP:
          - converte as colns de datas para o tipo datetime.
          - convrt colns com pocs valrs unicos para o tipo 'catgry' (ex.: 'sitc', 'nome do cedente', etc.).
          - calcla e armzn o totl de 'valor atul' para evitar recmpt.

        
        parametros:
            df cntd os dados financeiros.
            data de referencia para os calcls.
                se nao fornecida, utiliza a data atual.
        """
        # cria uma copia para nao aftr o df original
        self.df = df.copy()

        # convrt colns de data (ve se existam) pra o tipo dattm
        date_cols = ['Data de Vencimento Ajustada', 'Data de Vencimento', 'Data de Emissão', 'Data de Aquisição']
        for col in date_cols:
            if col in self.df.columns:
                self.df[col] = pd.to_datetime(self.df[col], errors='coerce') #coerce  eu sempre boto pra inputar nan
#

        # define a data de referencia
        self.data_referencia = pd.to_datetime(data_referencia) if data_referencia else pd.to_datetime('today')
##  se ele nao receber a data de referenia ele usa a atual. Esto mais acostumado com pd datetime

        # otmza colns categoricas convrt-as para o tipo 'catgry'
        #  >>Acho que isso melhora a velocidade da groupby, por ex 
        cat_cols = [
            'Situação', 'Nome do Cedente', 'Nome do Sacado', 
            'CAPAG Ente', 'Nome do Ente Consignado', 'Nome do Originador',
            'Tipo de Recebível'
        ]
        for col in cat_cols:
            if col in self.df.columns:
                self.df[col] = self.df[col].astype('category')


        # calc o total de 'valor atual' pra nao ter que reprocessar
        # >>tipo, isso não faz tanta diferença, mas notei q tava repetindo nas fçs
        if 'Valor Atual' in self.df.columns:
            self.total_valor_atual = self.df['Valor Atual'].sum()
        else:
            self.total_valor_atual = 0
        #adicionar a lista se quiser (da pra testar sem)
        if feriados:
            # Garante que é um array de timestamps
            feriados = pd.to_datetime(feriados, errors='coerce')

            # Remove valores NaT, converte para numpy.array e depois para o tipo datetime64[D]
            self.feriados = feriados.dropna().to_numpy().astype('datetime64[D]')
        else:
            self.feriados = np.array([], dtype='datetime64[D]')




# adiciona as colunas calculadas de forma automática, se chamar a classe
        self.adicionar_colunas()
##

    def adicionar_colunas(self):
        """
        adicn novs colns ao datfrm:
          - 'prazo dias uteis2': numero de dias uteis entre 'data de vencimento ajustd'
            e a data de refrnc (utilzn uma operacao vetorizada).
          - 'przo dias corrds': diferenca (em dias) entre 'data de vencmn ajustada' e a data de referencia.
          - 'valr liqdo atual': difrnc entre 'valor atul' e 'valr de pdd'.
        """
        if 'Data de Vencimento Ajustada' in self.df.columns:
            # convrt a data de referencia e os valores da colna para numpy.datt 64 cmo unidade 'd'
            start_date = np.datetime64(self.data_referencia, 'D')
            end_dates = self.df['Data de Vencimento Ajustada'].values.astype('datetime64[D]')
##
            
            # calculo vetrzd de dias utes
            # aqui usa a busfays pra evitar ter q interar com for
            self.df['Prazo Dias Úteis2'] = np.busday_count(start_date, end_dates, holidays=self.feriados)
            self.df['Prazo Dias Corridos'] = (self.df['Data de Vencimento Ajustada'] - self.data_referencia).dt.days
#

        if 'Valor Atual' in self.df.columns and 'Valor de PDD' in self.df.columns:
            self.df['Valor Líquido Atual'] = self.df['Valor Atual'] - self.df['Valor de PDD']


        return self.df


    def calcular_metricas(self):
        """
        calcla divrss mehtricas financeiras a partir do dataframe.
##

        retorna:
            dict: dicionario contnd as metricas 
        """
        metricas = {}
##

        # concentracao da carteira: cedente e sacado
        if self.total_valor_atual:
            metricas['Concentração por Cedente'] = (
                self.df.groupby('Nome do Cedente',observed=False)['Valor Atual'].sum() / self.total_valor_atual
            )
            metricas['Concentração por Sacado'] = (
                self.df.groupby('Nome do Sacado',observed=False)['Valor Atual'].sum() / self.total_valor_atual
            )
        else:
            metricas['Concentração por Cedente'] = None
            metricas['Concentração por Sacado'] = None
##

        # przo mehdo da cartr (duration)
        if 'Prazo Dias Corridos' in self.df.columns:
            self.df['Peso'] = self.df['Valor Atual'] * self.df['Prazo Dias Corridos']
            metricas['Prazo Médio da Carteira (Dias)'] = (
                self.df['Peso'].sum() / self.total_valor_atual if self.total_valor_atual else None
            )
#

        # indce de inadmp 
        #aqui ele evita divisao pro zero com o if, e faz filtro vetorizado
        if 'Situação' in self.df.columns:
            vencidos = self.df[self.df['Situação'] == 'Vencido']
            metricas['Índice de Inadimplência (%)'] = (
                (vencidos['Valor Atual'].sum() / self.total_valor_atual * 100) if self.total_valor_atual else None
            )
##

        # taxa mehda (assumindo que 'taxa du eq ano' existe)
        if 'Taxa DU EQ Ano' in self.df.columns:
            metricas['Taxa Média (%)'] = self.df['Taxa DU EQ Ano'].mean() * 100


        # volume por capg, ente e originador
        if 'CAPAG Ente' in self.df.columns:
            metricas['Volume por CAPAG'] = self.df.groupby('CAPAG Ente',observed=False)['Valor Atual'].sum()
        if 'Nome do Ente Consignado' in self.df.columns:
            metricas['Volume por Ente'] = self.df.groupby('Nome do Ente Consignado',observed=False)['Valor Atual'].sum()
        if 'Nome do Originador' in self.df.columns:
            metricas['Volume por Originador'] = self.df.groupby('Nome do Originador',observed=False)['Valor Atual'].sum()
#

        return metricas
#

    def calcular_estatisticas(self):
        """
        calcula contagens, maximos e minms de diversas colns do dataframe.
#

        retrna:
            dict: dicnr contnd as esttst calcld.
        """
        estatisticas = {}
#

        # contagens
        estatisticas['Quantidade de Tipos de Recebível'] = (
            self.df['Tipo de Recebível'].nunique() if 'Tipo de Recebível' in self.df.columns else None
        )
        estatisticas['Quantidade de Códigos de Contrato'] = (
            self.df['Código do Contrato'].nunique() if 'Código do Contrato' in self.df.columns else None
        )
        estatisticas['Quantidade de Participantes'] = (
            self.df['Número do Participante'].nunique() if 'Número do Participante' in self.df.columns else None
        )
        estatisticas['Quantidade de Cedentes'] = (
            self.df['Documento do Cedente'].nunique() if 'Documento do Cedente' in self.df.columns else None
        )
        estatisticas['Quantidade de Datas de Aquisição'] = (
            self.df['Data de Aquisição'].nunique() if 'Data de Aquisição' in self.df.columns else None
        )
        estatisticas['Quantidade de Situações'] = (
            self.df['Situação'].nunique() if 'Situação' in self.df.columns else None
        )
        estatisticas['Quantidade de Entes Consignados'] = (
            self.df['Documento do Ente Consignado'].nunique() if 'Documento do Ente Consignado' in self.df.columns else None
        )
        estatisticas['Quantidade de UFs de Ente'] = (
            self.df['UF Ente'].nunique() if 'UF Ente' in self.df.columns else None
        )
        estatisticas['Quantidade de Originadores'] = (
            self.df['Documento do Originador'].nunique() if 'Documento do Originador' in self.df.columns else None
        )
##

        # maximos
        estatisticas['Maior Número de Parcela'] = (
            self.df['Numero da Parcela'].max() if 'Numero da Parcela' in self.df.columns else None
        )
        estatisticas['Maior Quantidade de Parcelas'] = (
            self.df['Quantidade de Parcelas'].max() if 'Quantidade de Parcelas' in self.df.columns else None
        )
        estatisticas['Maior Data de Emissão'] = (
            self.df['Data de Emissão'].max() if 'Data de Emissão' in self.df.columns else None
        )
        estatisticas['Maior Data de Aquisição'] = (
            self.df['Data de Aquisição'].max() if 'Data de Aquisição' in self.df.columns else None
        )
        estatisticas['Maior Data de Vencimento Ajustada'] = (
            self.df['Data de Vencimento Ajustada'].max() if 'Data de Vencimento Ajustada' in self.df.columns else None
        )
        estatisticas['Maior Valor de Contrato'] = (
            self.df['Valor de Contrato'].max() if 'Valor de Contrato' in self.df.columns else None
        )
        estatisticas['Maior Valor de Compra'] = (
            self.df['Valor de Compra'].max() if 'Valor de Compra' in self.df.columns else None
        )
        estatisticas['Maior Valor Atual'] = (
            self.df['Valor Atual'].max() if 'Valor Atual' in self.df.columns else None
        )
        estatisticas['Maior Valor de Vencimento'] = (
            self.df['Valor de Vencimento'].max() if 'Valor de Vencimento' in self.df.columns else None
        )
        estatisticas['Maior Valor de Vencimento Atualizado'] = (
            self.df['Valor de Vencimento Atualizado'].max() if 'Valor de Vencimento Atualizado' in self.df.columns else None
        )
        estatisticas['Maior Valor Líquido Atual'] = (
            self.df['Valor Líquido Atual'].max() if 'Valor Líquido Atual' in self.df.columns else None
        )
        if 'Valor Atual' in self.df.columns and 'Valor de PDD' in self.df.columns:
            percentual_pdd = self.df['Valor de PDD'] / self.df['Valor Atual'].replace(0, np.nan)
            estatisticas['Maior Percentual de PDD sobre Valor Atual (%)'] = percentual_pdd.max() * 100
        else:
            estatisticas['Maior Percentual de PDD sobre Valor Atual (%)'] = None
        estatisticas['Maior Taxa da Operação por DU'] = (
            self.df['Taxa da Operação por DU'].max() if 'Taxa da Operação por DU' in self.df.columns else None
        )
        estatisticas['Maior Taxa DU EQ Mês'] = (
            self.df['Taxa DU EQ Mês'].max() if 'Taxa DU EQ Mês' in self.df.columns else None
        )
        estatisticas['Maior Taxa DU EQ Ano'] = (
            self.df['Taxa DU EQ Ano'].max() if 'Taxa DU EQ Ano' in self.df.columns else None
        )
        estatisticas['Maior Prazo Dias Úteis2'] = (
            self.df['Prazo Dias Úteis2'].max() if 'Prazo Dias Úteis2' in self.df.columns else None
        )
##

        return estatisticas
#

    def concentracao_por_cedente_sacado(self):
        """
        calcula a concnt da cartr por cedente e sacdo.
##
        
        retrna:
            dict: dicionario com a concnt percnt por 'nome do cednte' e 'nome do sacado'.
        """
        if self.total_valor_atual:
            concentracao_cedente = (
                self.df.groupby('Nome do Cedente', observed=False)['Valor Atual'].sum() / self.total_valor_atual * 100
            ).sort_values(ascending=False)
            concentracao_sacado = (
                self.df.groupby('Nome do Sacado', observed=False)['Valor Atual'].sum() / self.total_valor_atual * 100
            ).sort_values(ascending=False)
        else:
            concentracao_cedente = concentracao_sacado = None


        return {
            'cedente': concentracao_cedente,
            'sacado': concentracao_sacado
        }
##

    def prazo_medio_ponderado(self):
        """
        calcula o przo mehdio pondrd da carteira.
#
        
        retrna:
            flot: prazo mehdo pondrd (em dias).
        """
        if 'Data de Vencimento' in self.df.columns and 'Valor Atual' in self.df.columns:
            # usa a data atual para calcular os dias ateh o vencmn
            dias_ate_vencimento = (self.df['Data de Vencimento'] - pd.Timestamp.today()).dt.days
            return np.average(dias_ate_vencimento, weights=self.df['Valor Atual'])
         # Prazo Médio = (Σ (dias_ate_vencimento * Valor Atual)) / Σ (Valor Atual)
        return None


    def indice_inadimplencia(self):
        """
        calcula o indice de inadmp da cartr.
##
        
        retorna:
            float: percentual de dirts creditorios inadimplentes.
        """
        if 'Situação' in self.df.columns and 'Valor Atual' in self.df.columns:
            inadimplentes = self.df[self.df['Situação'] == 'Inadimplente']['Valor Atual'].sum()
            return (inadimplentes / self.total_valor_atual * 100) if self.total_valor_atual else None
        return None


    def taxa_media(self):
        """
        calcula a taxa mehdia pondrd da carteira.

        
        retorna:
            flot: taxa mehda ponderada.
        """
        if 'Taxa da Operação por DU' in self.df.columns and 'Valor Atual' in self.df.columns:
            return np.average(self.df['Taxa da Operação por DU'], weights=self.df['Valor Atual'])
        # Taxa Média = (Σ (Taxa da Operação por DU * Valor Atual)) / Σ (Valor Atual)
        return None
#

    def volume_por_categoria(self, categoria):
        """
        calcula o volme totl da carteira por uma categoria especifica.
#

        parametros:
            catgr (str): nome da colna para agrupar os dads (ex.: 'capg ente', 'nome do ente consignado', 'nome do orignd').


        retrna:
            pd.series: sehrie com o volume total por categoria.
        """
        if categoria in self.df.columns:
            return self.df.groupby(categoria, observed=False)['Valor Atual'].sum().sort_values(ascending=False)
        return None
##

#REFERÊNCIAS: #convrs de colunas para o tipo categorico:
#https://stackoverflow.com/questions/38088652/convert-pandas-column-to-categorica#uso de operacoes vetrzd para melhrr a performance:
#https://pt.stackoverflow.com/questions/490894/otimiza%C3%A7%C3%A3o-percorrendo-dataframe-pandas
#https://pt.stackoverflow.com/questions/353124/performance-ruim-ao-percorrer-uma-matriz
#

#uso de grpby para agrgcs eficientes:
#https://stackoverflow.com/questions/19384532/how-to-count-number-of-rows-per-group-and-other-statistics-in-pandas-group-by


#conversao de colunas de data para o tipo datetime:
#https://stackoverflow.com/questions/29314033/python-pandas-convert-datetime-column-to-string-exactly-in-format-yyyymmddhhmmss
#

#uso de pd.to_dtt para manipulacao de dats:
#https://stackoverflow.com/questions/21269399/difference-between-datetime-today-datetime-now-and-datetime-utcnow
#

#calclo de mehds moveis e outrs opercs com rollng windows:
#https://stackoverflow.com/questions/19900202/computing-rolling-mean-of-time-series-data-using-pandas
#

#filtragem de datfrm com multpl condcs:
#https://pt.stackoverflow.com/questions/508528/filtrar-dataframe-pandas-com-duas-ou-mais-condi%C3%A7%C3%B5es



