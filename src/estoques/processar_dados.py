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
class ProcessarDados:
    def __init__(self, df_final):
        """Inicializa a classe com o DataFrame processado.
        
        Parâmetros:
        df_final (pd.DataFrame): DataFrame com os dados financeiros processados.
        """
        self.df_final = df_final
    def dist_capag(self, class_col: str, col_valor: str) -> pd.Series:
        """Calcula a distribuição de valores agrupados por classificação de CAPAG.
        
        Parâmetros:
        class_col (str): Nome da coluna categórica para agrupar os dados.
        col_valor (str): Nome da coluna com valores numéricos a serem somados.
        
        Retorna:
        pd.Series: S´rie com os valores agregados por categoria.
        
        Exemplo de uso:
        processador.dist_capag('CAPAG Ente', 'Valor Atual')
        """
        return self.df_final.groupby(class_col, observed=True)[col_valor].sum()
    
    def custom_fill2(self, col1: pd.Series, col2: pd.Series) -> list:
        """Preenche valores nulos com base em outra coluna.
        
        pars:
        col1 (pd.Series): Serie de entrada principal.
        col2 (pd.Series): Serie auxiliar para preenchimento.
        
        Returna:
        list: Lista de valores preenchidos.
        
        Exemplo de uso:
        processador.custom_fill2(df['CAPAG Ente'], df['UF Ente'])
        """
        return [v1 if pd.notna(v1) else ('A' if v2 == 'BR' else 'Outros') for v1, v2 in zip(col1, col2)]
    
    def vencimento_anual(self, col_valor: str, col_vcto: str) -> tuple:
        """Calcula vencimentos anuais acumulados.
        
        args:
        col_valor (str): Nome da coluna com os valores monetários.
        col_vcto (str): Nome da coluna com as datas de vencimento.
        
        retorna:
        tuple: (Série com valores anuais, Série acumulada)
        
        Ex
        df2, df3 = processador.vencimento_anual('Valor de Vencimento', 'Data de Vencimento')
        """
        df_aberto = self.df_final[self.df_final['Situação'] == 'A Vencer'].copy()
        df_aberto['VCTO_ANO'] = df_aberto[col_vcto].dt.year
        df2 = df_aberto.groupby('VCTO_ANO',observed=False)[col_valor].sum()
        df3 = df2.cumsum() / df2.sum()
        return df2, df3
    
    def concentracao_sacado(self, col_valor: str, col_class: str, cutoffs: list) -> dict:
        """calc a concentração de valores por sacado.
        adaptado do nb Felipe
        
        args:
        col_valor (str): Nome da coluna com os valores a serem agregados.
        col_class (str): Nome da coluna categórica para agrupamento.
        cutoffs (list): Lista de cortes para agrupar os maiores sacados.
        
        Retorn:
        dict: Dicionário com a soma dos valores para cada corte.
        
        Exemplo de uso:
        processador.concentracao_sacado('Valor Atual', 'Documento do Sacado', [10, 20, 50])
        """
        df11 = self.df_final.groupby(col_class, observed=False)[col_valor].sum().sort_values(ascending=False)
        df11 = df11 / df11.sum()
        return {f'{c} maiores': df11[:c].sum() for c in cutoffs}
    
    def pagamentos_por_ano(self) -> pd.Series:
        """Agrupa pagamentos por ano de vencimento.
        
        Retorn:
        pd.Series: Série com valores totais por ano de vencimento.
       
        """
        xs = pd.Series(self.df_final['Data de Vencimento'].unique())
        ys = xs.dt.strftime('%Y')
        map_year = dict(zip(xs, ys))
        series = self.df_final['Data de Vencimento'].map(map_year)
        return self.df_final.groupby(series, observed=False)['Valor Atual'].sum().sort_index()


    def fluxo_pagamento(self, horizonte: str) -> pd.Series:
        """Calcula o fluxo de pagamento agrupado por diferentes horizontes.
        OBS: ELE PEGA no FUTURO
        Parâmetros:
        horizonte (str): Pode ser 'dia', 'semana' ou 'mês'.
        
        Retorna:
        pd.Series: Série com os valores totais de pagamento no horizonte escolhido.
        
        Ex:
         processador.fluxo_pagamento('mês'), podia ser semana 
        """
        if horizonte == 'dia':
            series = self.df_final['Data de Vencimento'].dt.strftime('%Y-%m-%d')
        elif horizonte == 'semana':
            series = self.df_final['Data de Vencimento'].dt.strftime('%Y-%W')
        elif horizonte == 'mês':
            series = self.df_final['Data de Vencimento'].dt.strftime('%Y-%m')
        else:
            raise ValueError("Horizonte inválido. Use 'dia', 'semana' ou 'mês'.")
        
        return self.df_final.groupby(series, observed=False)['Valor Atual'].sum().sort_index()
    
    def percentual_pdd(self) -> float:
        """calc o pcentual de PDD em relação ao valor total.
        
        Retorna:
        float: Percentual de PDD sobre o total do valor atual.

        """
        return (self.df_final['Valor de PDD'].sum() / self.df_final['Valor Atual'].sum()) * 100
    
    def taxa_media(self) -> float:
        """calc a tx média das operações.
        
        Retorna:
        float: Média das taxas de operação ponderada pelo valor atual, através da tx da OP
                ()
        """
        return (self.df_final['Taxa da Operação por DU'] * self.df_final['Valor Atual']).sum() / self.df_final['Valor Atual'].sum()
    
    def volume_por_categoria(self, categoria: str) -> pd.Series:
        """Calcula o volume de valores agrupados por uma categoria específica.
        
        Parâmetros:
        categoria (str): Nome da coluna categorica pra agrupamento.
        
        Retorna:
        pd.Series: Série com os volumes agrupados.
        
        Exemplo de uso:
         processador.volume_por_categoria('CAPAG Ente')
        """
        if categoria not in self.df_final.columns:
            raise ValueError(f"Categoria '{categoria}' não encontrada no DataFrame.")
        
        return self.df_final.groupby(categoria, observed=False)['Valor Atual'].sum().sort_values(ascending=False)



'''
# Ex uso:
processador = ProcessarDados(df_final)
fluxo_mensal = processador.fluxo_pagamento('mês')
pdd_percentual = processador.percentual_pdd()
taxa_media_op = processador.taxa_media()
volume_capag = processador.volume_por_categoria('CAPAG Ente')

# crndo a instancia da clsse com o dataframe final processado
processador = ProcessarDados(df_final)
# calculando vencmn anus
df_vencimentos, df_cumulativo = processador.vencimento_anual('Valor de Vencimento', 'Data de Vencimento Ajustada')
# calcln concnt de sacado
cutoffs = [10, 20, 50, 100, 200, 500, 1000]
concentracao_sacado = processador.concentracao_sacado('Valor Atual', 'Documento do Sacado', cutoffs)
# calcln pagmnt por data
pagamentos_por_data = processador.pagamentos_por_data()
# mostrn os resltd
print(df_vencimentos)
print(concentracao_sacado)
print(pagamentos_por_data)
'''
