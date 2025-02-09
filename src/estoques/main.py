# main.py
#from estoques import ProcessadorPastas, ImportarDados, ProcessarDados, ProcessarMetricas
from processador_pastas import ProcessadorPastas
from importador_dados import ImportadorDados
from processar_dados import ProcessarDados
from processar_metricas import ProcessarMetricas
import pandas as pd

    ################### MAIN   #######################################
    #######################   Config  ######################################
def main():    
    pd.options.display.max_columns = 100     ## para não abusar do rolling e travar o notebook quando testando
    today = pd.Timestamp.now().normalize()
    ##########################################################################
    #data_path = '../data'  # caminho padrão para dados se nenhum for fornecido 
    ##################################################################

    #################################################################
    # Uso do objeto ProcessadorPastas################################
    obj_pastas = ProcessadorPastas(ignore_list=[], ultima=False)#### aqui poderia colocoar o datapath #############################
    #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #
    print("Pasta Selecionada:", obj_pastas.pasta_selecionada)##########
    list_files= obj_pastas.files_last_folder() ######################
    #################################################################
    # Uso do objeto ImportadorDados##################################
    obj_importador = ImportadorDados()###############################
    #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #
    list_holidays= obj_importador.holidays
    ref_date=obj_importador.ref_date
    #print("Feriados carregados:", importador.holidays)
    #print("Data de referência:", importador.ref_date)
    #print("Último dia útil do mês anterior:", importador.eom_date)
    print(list_files)
    df_final= obj_importador.importar_dados(list_files)
    #################################################################
    #### Primeiros procs: ###########################################
    ##################### objeto: proc dados  ######################
    obj_proc_dados= ProcessarDados(df_final) ########################
    #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #
    print(obj_proc_dados.taxa_media()) ##############################
    #print(obj_proc_dados.fluxo_pagamento('mês'))
    #print(pdd_percentual = obj_proc_dados.percentual_pdd())
    #print(taxa_media_op = obj_proc_dados.taxa_media())
    #print(volume_capag = obj_proc_dados.volume_por_categoria('CAPAG Ente'))
    #### Procs ATUAIS: ###############################################
    obj_proc_metricas = ProcessarMetricas(df_final, ref_date, list_holidays)#########
    #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #
    df_atualizado = obj_proc_metricas.adicionar_colunas()
    print("DataFrame atualizado com novas colunas...")
    #print(df_atualizado.head())
    metricas = obj_proc_metricas.calcular_metricas()
    print("\nMétricas calculadas:")
    for chave, valor in metricas.items():
        print(f"{chave}: {valor}")

    estatisticas = obj_proc_metricas.calcular_estatisticas()
    print("\nEstatísticas calculadas:")
    for chave, valor in estatisticas.items():
        print(f"{chave}: {valor}")
    concentracao = obj_proc_metricas.concentracao_por_cedente_sacado()
    print("\nConcentração por Cedente:")
    print(concentracao['cedente'])
    print("\nConcentração por Sacado:")
    print(concentracao['sacado'])
    prazo_medio = obj_proc_metricas.prazo_medio_ponderado()
    print(f"\nPrazo Médio Ponderado da Carteira: {prazo_medio} dias")
    indice_inadimplencia = obj_proc_metricas.indice_inadimplencia()
    print(f"\nÍndice de Inadimplência: {indice_inadimplencia:.2f}%")
    taxa_media = obj_proc_metricas.taxa_media()
    print(f"\nTaxa Média Ponderada da Carteira: {taxa_media:.2f}%")
    volume_por_capag = obj_proc_metricas.volume_por_categoria('CAPAG Ente')
    print("\nVolume por CAPAG Ente:")
    print(volume_por_capag)


if __name__ == '__main__':
    main()
