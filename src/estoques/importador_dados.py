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

class ImportadorDados:
    def __init__(self):
        """iniclz o imprtd, busca o arquivo de ferds automaticamente e defne dats de refrnc."""
        self.repo_root = self.encontrar_repo_root()
        self.arquivo_feriados = self.encontrar_arquivo_feriados()
        self.holidays = self.carregar_feriados()
        self.definir_datas_referencia()

    def encontrar_repo_root(self):
        """sobe diretorios ateh encntr o repositorio raiz."""
        current_dir = os.getcwd()
        while current_dir:
            parent_dir = os.path.dirname(current_dir)
            # se estivermos em uma pasta "notebooks", sobe um nivl
            if 'notebooks' in os.path.basename(current_dir).lower():
                current_dir = parent_dir
            # verifica se ha arquivos no dirtr (sinal de que pode ser o repstr raiz)
            if any(os.path.isfile(os.path.join(current_dir, f)) for f in os.listdir(current_dir)):
                return current_dir
            if parent_dir == current_dir:
                break  # chegou a raiz do sistma
            current_dir = parent_dir
        print("Repositório raiz não encontrado.")
        return os.getcwd()


    def encontrar_arquivo_feriados(self):
        """procura o arquivo de feriados autmtc no repstr, considerando nomes similares."""
        print(f"Procurando arquivos em: {self.repo_root}")
        all_files = glob.glob(os.path.join(self.repo_root, '**', '*'), recursive=True)
        print(f"Arquivos encontrados: {len(all_files)}")
        target_name = "feriados_nacionais.xls"
        candidates = []
        for file in all_files:
            file_name = os.path.basename(file).strip()
            if file_name.lower() == target_name.lower():
                print(f"Arquivo de feriados encontrado exatamente: {file}")
                return file
            similarity = fuzz.partial_ratio(target_name.lower(), file_name.lower())
            if similarity > 80:
                candidates.append((file, similarity))
        if candidates:
            best_match = max(candidates, key=lambda x: x[1])[0]
            print(f"Arquivo de feriados encontrado por similaridade: {best_match}")
            return best_match
        print("Arquivo de feriados não encontrado.")
        return None
##

    def carregar_feriados(self):
        """carrega os feriados a partr do arquivo encntr e remve linhs invalidas."""
        if not self.arquivo_feriados:
            print("Nenhum arquivo de feriados disponível para importação.")
            return []
        df_feriados = pd.read_excel(self.arquivo_feriados)
        df_feriados['Data'] = pd.to_datetime(df_feriados['Data'], errors='coerce')
        df_valid = df_feriados.dropna(subset=['Data'])
        return df_valid['Data'].tolist()
#

    def definir_datas_referencia(self):
        """defne as dats de referencia para selecao do estqe."""
        today = pd.Timestamp.now().normalize()
        custom_bd = pd.offsets.CustomBusinessDay(holidays=self.holidays)
        self.eom_date = today - pd.offsets.BMonthEnd(1)  # ultimo dia util do mes antrr
        self.ref_date = today - pd.offsets.BMonthBegin(1) - 1 * custom_bd  # data de refrnc ajustd
        print(f"Data de referência definida: {self.ref_date}")
#

    def importar_dados(self, list_files):
        """le varios arquivos csv grnds e aplica otimizacoes de memoria."""
        # definicao das colns por grupo
        no_data_cols = ['Código da Parcela',
                        'Código na Registradora',
                        'Documento da Registradora',
                        'Nome da Registradora',
                        'Chave NFE/CTE',
                        'Código de Averbação']
##

        one_data_cols = ['Fundo', 
                         'CNPJ Fundo', 
                         'Data do Movimento',
                         'Tipo da Operação']
#

        cat_cols = ['Tipo de Recebível',
                    'Nome do Recebível',
                    'Código do Contrato',
                    'Documento do Cedente',
                    'Nome do Cedente',
                    'Documento do Sacado',
                    'Nome do Sacado',
                    'Situação',
                    'Risco',
                    'Aval',
                    'Classificação do Sacado',
                    'Classificação da Parcela',
                    'Nome do Ente Consignado',
                    'Documento do Ente Consignado',
                    'UF Ente',
                    'CAPAG Ente',
                    'Nome do Originador',
                    'Documento do Originador']


        date_cols = ['Data de Emissão',
                     'Data de Aquisição',
                     'Data de Vencimento',
                     'Data de Vencimento Ajustada']
##

        float_cols = ['Valor de Contrato',
                      'Valor de Compra',
                      'Valor Atual',
                      'Valor de Vencimento',
                      'Valor de PDD',
                      'Taxa do Arquivo',
                      'Taxa da Operação por DU',
                      'Valor de Vencimento Atualizado',
                      'Taxa DU EQ Mês',
                      'Taxa DU EQ Ano',
                      'TIR']
##

        int_cols = ['Numero da Parcela',
                    'Quantidade de Parcelas',
                    'Prazo Dias Úteis',
                    'Dias Corridos Vencidos']
##

        str_cols = ['Classificação da Parcela',
                    'Número do Participante',
                    'Nosso Número Bancário',
                    'Nome da Registradora',
                    'Nome do Recebível',
                    'Código do Contrato',
                    'UF Ente']
#

        # definindo dtypes para colns de string (para reduzir conversoes postrr)
        dtypes = {col: 'str' for col in str_cols}
#

        # calcular a unio de tods as colns necessarias
        usecols = list(set(one_data_cols + no_data_cols + cat_cols + date_cols + float_cols + int_cols + str_cols))
#

        # dicionario para armazenar os valrs unicos das colns constantes por arqvo
        dict_data = {col: [] for col in one_data_cols + no_data_cols}
        all_dfs = []
        all_cols = None


        for i, file in enumerate(list_files, 1):
            print(f"Lendo arquivo {i}/{len(list_files)}: {file}")
            reader = pd.read_csv(file,
                                 encoding='latin_1',
                                 sep=';',
                                 parse_dates=date_cols,
                                 dayfirst=True,
                                 dtype=dtypes,
                                 chunksize=50000,
                                 usecols=usecols,
                                 low_memory=True)
            for chunk in reader:
                if all_cols is None:
                    all_cols = dict(enumerate(chunk.columns))
##

                # processar colns que devm ter um unico valr por chnk
                for col in one_data_cols:
                    unique_vals = chunk[col].unique()
                    if len(unique_vals) > 1:
                        raise AssertionError(f'Coluna {col} possui mais de um dado no chunk')
                    dict_data[col].append(unique_vals[0])
                    chunk.drop(columns=[col], inplace=True)


                # processar colns que serao ignrds (mas regstr)
                for col in no_data_cols:
                    # se a colna tivr algum dado (podrms regstr um warnng, se necessario)
                    if chunk[col].nunique() > 0:
                        pass  # opcnl: regstr aviso
                    dict_data[col].append('')
                    chunk.drop(columns=[col], inplace=True)
#

                # convrt colunas de float: utiliza vectorized string replace (se necssr) e conversao
                for col in float_cols:
                    if col in chunk.columns:
                        if chunk[col].dtype == object:
                            chunk[col] = chunk[col].str.replace(',', '.', regex=False)
                        chunk[col] = chunk[col].astype('float32')


                # convrt colns de int
                for col in int_cols:
                    if col in chunk.columns:
                        chunk[col] = chunk[col].astype('int32')
#

                all_dfs.append(chunk)
                del chunk  # libra memra do chnk
#

        print("Leitura de arquivos concluída. Concatenando os DataFrames...")
        df_final = pd.concat(all_dfs, ignore_index=True)
##

        # converter colunas categoricas para otimzc de memra
        for col in cat_cols:
            if col in df_final.columns:
                df_final[col] = df_final[col].astype('category')
#

        # valdc de unicidade em colns imprtn (opcional)
        if set(['Número do Participante', 'Nosso Número Bancário']).issubset(df_final.columns):
            df_temp = df_final[['Número do Participante', 'Nosso Número Bancário']].drop_duplicates()
            if df_temp.shape != df_final[['Número do Participante', 'Nosso Número Bancário']].shape:
                raise AssertionError("Os valores de 'Número do Participante' e 'Nosso Número Bancário' não são únicos por linha.")
##

        print("Leitura e processamento concluídos.")
        return df_final
##

