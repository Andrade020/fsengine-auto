import os                                                   # Custos tabulariorum
import glob                                                 # Venator formarum
import json                                                 # Narrator historiarum
import pandas as pd                                         # Alchimista datorum

from estoques.processador_pastas import ProcessadorPastas   # Architectus viarum
from estoques.importador_dados import ImportadorDados       # Navigator maris digitalis
from estoques.processar_dados import ProcessarDados         # Artifex sapiens
from estoques.processar_metricas import ProcessarMetricas   # Magister precisionis


def main():
    # Config inic ###$$##$$##$$##$$##$$##$$##$$##$$##$$##$$##$$$###$$$##$#$#$$$#$##$#$
    pd.options.display.max_columns = 100 ##$#$#$#$#$#$$#$$#$$##$#$$#$$#$#$#$#$#$$#$#$#
    # Instancia o ProcessadorPastas para identific pastas válidas na pasta "data"
    obj_pastas = ProcessadorPastas(ignore_list=[], ultima=True)
    data_path = obj_pastas.file_path ###$$##$$##$$##$$####$$##$$##$$##$$#
    valid_folders = obj_pastas.valid_folders  # pastas válidas já filtradas e ordenadas
###$$##$$##$$##$$####$$##$$##$$##$$####$$##$$##$$##$$####$$##$$##$$##$$#
    if not valid_folders:
        print("Nenhuma pasta válida encontrada em 'data'.")
        return
###$$##$$##$$##$$####$$##$$##$$##$$####$$##$$##$$##$$#
    # Cria a pasta p salvar os resuls, se n existir
    results_dir = os.path.join(os.getcwd(), "results")
    os.makedirs(results_dir, exist_ok=True)
###$$##$$##$$##$$####$$##$$##$$##$$#
    # Arquivo cas pastas jah processadas
    processed_file = os.path.join(results_dir, "processed_folders.json")
    if os.path.exists(processed_file):
        with open(processed_file, "r", encoding="utf-8") as pf:
            processed_folders = json.load(pf)
    else:
        processed_folders = []
###$$##$$##$$##$$####$$##$$##$$##$$####$$##$$##$$##$$####$$##$$##$$##$$#
    # laço p/ cada pasta válida que ainda n foi processada
    for folder in valid_folders:
        if folder in processed_folders:
            print(f"Pasta {folder} já foi processada. Ignorando.")
            continue
###$$##$$##$$##$$####$$##$$##$$##$$####$$##$$##$$##$$####$$##$$##$$##$$#
        print(f"\nProcessando pasta: {folder}")
        folder_path = os.path.join(data_path, folder)
        list_files = glob.glob(os.path.join(folder_path, '*'))
        if not list_files:
            print(f"Pasta {folder} sem arquivos. Ignorando.")
            continue
###$$##$$##$$##$$####$$##$$##$$##$$####$$##$$##$$##$$####$$##$$##$$##$$#
        # Importa parâms (feriados, data de referência, etc.) e os dados
        obj_importador = ImportadorDados()
        list_holidays = obj_importador.holidays
        ref_date = obj_importador.ref_date
        df_final = obj_importador.importar_dados(list_files)
        if df_final.empty:
            print(f"Dados vazios na pasta {folder}. Ignorando.")
            continue
###$$##$$##$$##$$####$$##$$##$$##$$####$$##$$##$$##$$####$$##$$##$$##$$#
        # --- Processamento dos dados usando ProcessarDados ---
        obj_proc_dados = ProcessarDados(df_final)
        taxa_media_dados = obj_proc_dados.taxa_media()                   # escalar
        # Calc fluxo de pagamnto para os 3 horizos
        fluxo_pagamento_d = obj_proc_dados.fluxo_pagamento('dia')           # diário
        fluxo_pagamento_s = obj_proc_dados.fluxo_pagamento('semana')          # semanal
        fluxo_pagamento_m = obj_proc_dados.fluxo_pagamento('mês')             # mensal
        percentual_pdd = obj_proc_dados.percentual_pdd()                    # escalar
        taxa_media_op = obj_proc_dados.taxa_media()                         # escalar
        try:
            vencimentos, cumulativo_vencimentos = obj_proc_dados.vencimento_anual(
                'Valor de Vencimento', 'Data de Vencimento Ajustada'
            )  # duas séries
        except Exception as e:
            vencimentos, cumulativo_vencimentos = None, None
        concentracao_sacado_dados = obj_proc_dados.concentracao_sacado(
            'Valor Atual', 'Documento do Sacado', [10, 20, 50, 100, 200, 500, 1000]
        )  # dicionário
        pagamentos_por_ano = obj_proc_dados.pagamentos_por_ano()          # série
###$$##$$##$$##$$####$$##$$##$$##$$####$$##$$##$$##$$#
        # --- méhtricas usando ProcessarMetricas ---
        obj_proc_metricas = ProcessarMetricas(df_final, ref_date, list_holidays)
        metricas = obj_proc_metricas.calcular_metricas()                  # dicionário (com séries)
        estatisticas = obj_proc_metricas.calcular_estatisticas()             # dicionário (com valores e séries)
        concentracao = obj_proc_metricas.concentracao_por_cedente_sacado()     # dicionário com séries
        prazo_medio = obj_proc_metricas.prazo_medio_ponderado()              # escalar
        indice_inadimplencia = obj_proc_metricas.indice_inadimplencia()        # escalar
        taxa_media_metricas = obj_proc_metricas.taxa_media()                 # escalar
        volume_por_capag = obj_proc_metricas.volume_por_categoria('CAPAG Ente')# série
###$$##$$##$$##$$####$$##$$##$$##$$####$$##$$##$$##$$####$$##$$##$$##$$####$$##$$##$$##$$#
        # --- Convrsão de Series para dics ---
        def series_to_dict(x):
            return x.to_dict() if hasattr(x, "to_dict") else x
###$$##$$##$$##$$####$$##$$##$$##$$####$$##$$##$$##$$####$$##$$##$$##$$####$$##$$##$$##$$#
        metricas = {k: series_to_dict(v) for k, v in metricas.items()}
        estatisticas = {k: series_to_dict(v) for k, v in estatisticas.items()}
        if concentracao:
            if 'cedente' in concentracao and hasattr(concentracao['cedente'], "to_dict"):
                concentracao['cedente'] = concentracao['cedente'].to_dict()
            if 'sacado' in concentracao and hasattr(concentracao['sacado'], "to_dict"):
                concentracao['sacado'] = concentracao['sacado'].to_dict()
        volume_por_capag = series_to_dict(volume_por_capag)
        fluxo_pagamento_d = series_to_dict(fluxo_pagamento_d)
        fluxo_pagamento_s = series_to_dict(fluxo_pagamento_s)
        fluxo_pagamento_m = series_to_dict(fluxo_pagamento_m)
        pagamentos_por_ano = series_to_dict(pagamentos_por_ano)
        if vencimentos is not None:
            vencimentos = series_to_dict(vencimentos)
        if cumulativo_vencimentos is not None:
            cumulativo_vencimentos = series_to_dict(cumulativo_vencimentos)

        # --- Monta o dic final de results ---
        results = {
            "folder": folder,
            "list_files": list_files,
            # Resltados de ProcessarDados
            "taxa_media_dados": taxa_media_dados,
            "fluxo_pagamento_diario": fluxo_pagamento_d,
            "fluxo_pagamento_semanal": fluxo_pagamento_s,
            "fluxo_pagamento_mensal": fluxo_pagamento_m,
            "percentual_pdd": percentual_pdd,
            "taxa_media_op": taxa_media_op,
            "vencimentos": vencimentos,
            "cumulativo_vencimentos": cumulativo_vencimentos,
            "concentracao_sacado_dados": concentracao_sacado_dados,
            "pagamentos_por_ano": pagamentos_por_ano,
            # Resltados de ProcessarMetricas
            "metricas": metricas,
            "estatisticas": estatisticas,
            "concentracao": concentracao,
            "prazo_medio": prazo_medio,
            "indice_inadimplencia": indice_inadimplencia,
            "taxa_media_metricas": taxa_media_metricas,
            "volume_por_capag": volume_por_capag
        }

        # --- Salva os resultados no JSON ---
        output_file = os.path.join(results_dir, f"results_{folder}.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4, default=str)
        print(f"Resultados salvos para a pasta {folder} em: {output_file}")

        # Adiciona a pasta proc a lista de pastas ja processdas 
        processed_folders.append(folder)
        with open(processed_file, "w", encoding="utf-8") as pf:
            json.dump(processed_folders, pf, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()
