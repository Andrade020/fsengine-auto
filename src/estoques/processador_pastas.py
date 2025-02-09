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
## IDEA atalização futura: recebe uma lista de pastas que já foram visitadas

class ProcessadorPastas:
    def __init__(self, file_path=None, ignore_list=None, ultima=False):
        """se fil_pt nao for forncd, busca autmtc pela pasta 'data'.
#
        
        parametros:
        file_path (str, opcional): caminho da pasta de dados.
        ignore_list (list, opcional): lista de datas (no formato 'yyyy-mm-dd') a serem ignoradas.
        ultima (bool, opcional): se True (padrão), seleciona a pasta mais recente;
                                 se False, seleciona a pasta mais antiga.
        """
        self.file_path = file_path if file_path else self.encontrar_data()
        self.ignore_list = set(ignore_list) if ignore_list else set()
        self.list_files = glob.glob(os.path.join(self.file_path, '*', '*.csv')) if self.file_path else []
        self.valid_folders = self.obter_pastas_validas()
        self.pasta_selecionada = self.obter_pasta(ultima)
#

    @staticmethod
    def nome_pasta_valido(nome_pasta):
        """verfca se o nome da pasta ta no formto yyyy-mm-dd."""
        try:
            datetime.strptime(nome_pasta, "%Y-%m-%d")
            return True
        except ValueError:
            return False


    def encontrar_data(self):
        """searcha  automaticamente a pasta 'Data' no diretorio do proj."""
        current_dir = os.getcwd()
        while current_dir:
            potential_path = os.path.join(current_dir, 'data')
            if os.path.isdir(potential_path):
                return potential_path
            parent_dir = os.path.dirname(current_dir)
            if parent_dir == current_dir:
                break  # chegamos a raiz do sistema
            current_dir = parent_dir
        print("Pasta 'data' não encontrada.")
        return None
##

    def obter_pastas_validas(self):
        """
        filtra e ordna as pastas que estejam no formto yyyy-mm-dd, removendo as que constm na ignr_l
        e descrt as pasts vazs (sem arqvs).
        a ordenacao eh feita de forma decrescente (mais recente para o mais antgo).
        """
        # obthm os nomes de pasta a partr dos arqvs csv encntr
        folder_names = {file.split(os.sep)[-2] for file in self.list_files}
        valid_folders = sorted(
            [
                folder for folder in folder_names
                if self.nome_pasta_valido(folder)
                and folder not in self.ignore_list
                and len(glob.glob(os.path.join(self.file_path, folder, '*'))) > 0
            ],
            key=lambda x: datetime.strptime(x, "%Y-%m-%d"),
            reverse=False  ###### Atenção- isso aqui gera uma ordem, que no caso preferi 
            ####################### deixr do mais antigo para o mais recente, atualmente 
        )
        return valid_folders





    def obter_pasta(self, ultima=False):
        """
        Retorna a pasta selecionada com base na opção.

        Parâmetros:
            ultima (bool): se True, retorna a pasta mais recente (primeiro da lista ordenada);
                           se False, retorna a pasta mais antiga (último da lista).
        """
        if not self.valid_folders:
            print("Nenhuma pasta válida encontrada.")
            return None
        return self.valid_folders[0] if ultima else self.valid_folders[-1]

    def files_last_folder(self, ultima=None):
        """
        Lista os arquivos da pasta escolhida.

        Parâmetros:
            ultima (bool, opcional):
                - se True, retorna os arquivos da pasta mais recente (primeiro da lista);
                - se False, retorna os arquivos da pasta mais antiga (último da lista);
                - se None, utiliza a pasta selecionada na inicialização (self.pasta_selecionada).

        Retorna:
            list: lista de caminhos dos arquivos na pasta escolhida.
        """
        if not self.valid_folders:
            print("Nenhuma pasta válida encontrada.")
            return []
        # Se o parâmetro não for informado, utiliza a pasta selecionada no __init__
        if ultima is None:
            folder = self.pasta_selecionada
        else:
            folder = self.valid_folders[0] if ultima else self.valid_folders[-1]
        caminho_pasta = os.path.join(self.file_path, folder)
        arquivos = glob.glob(os.path.join(caminho_pasta, '*'))
        return arquivos

