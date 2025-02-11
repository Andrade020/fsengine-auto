# fsengine-auto
open-source and licensed version of our analytics package for investment funds. It provides tools for automatically downloading datasets, performing analyses, and generating dashboards with key metrics. This version does not include sensitive data—users must have their own fund account with login credentials to adapt and utilize the package
# Processador de Dados de Estoque
datasaver.py
Sistema de processamento de dados de estoque que realiza análises e cálculos de métricas financeiras a partir de arquivos de dados.

## Funcionalidades

- Processamento automático de múltiplas pastas de dados
- Cálculo de diversas métricas financeiras:
  - Taxa média de operações
  - Fluxos de pagamento (diário, semanal e mensal)
  - Percentual de PDD
  - Análise de vencimentos
  - Concentração por sacado
  - Pagamentos por ano
  - Métricas de inadimplência
  - Prazos médios ponderados
  - Volume por CAPAG
  - E mais...
- Controle de pastas processadas para evitar reprocessamento
- Exportação dos resultados em formato JSON


## Estrutura do Projeto

```
.
├── datasaver.py
├── estoques/
│   ├── processador_pastas.py
│   ├── importador_dados.py
│   ├── processar_dados.py
│   └── processar_metricas.py
├── data/
│   └── YYYY-MM-DD/
│       └── arquivos_de_dados
└── results/
    ├── processed_folders.json
    └── results_YYYY-MM-DD.json
```

## Configuração

1. Clone o repositório
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Coloque seus arquivos de dados na pasta `data` em subpastas com formato de data (YYYY-MM-DD)

## Uso

Execute o script principal:

```bash
python main.py
```

O script irá:
1. Identificar pastas válidas em `data/`
2. Processar cada pasta não processada anteriormente
3. Calcular todas as métricas configuradas
4. Salvar os resultados em arquivos JSON na pasta `results/`

## Estrutura dos Resultados

Os resultados são salvos em arquivos JSON contendo:
- Informações da pasta processada
- Lista de arquivos processados
- Métricas calculadas por ProcessarDados
- Métricas calculadas por ProcessarMetricas
- Estatísticas e análises de concentração
- Índices e taxas calculadas

## Processamento de Dados

O sistema utiliza duas classes principais para processamento:

### ProcessarDados
- Cálculo de taxas médias
- Análise de fluxos de pagamento
- Cálculo de PDD
- Análise de vencimentos
- Concentração por sacado

### ProcessarMetricas
- Cálculo de métricas financeiras
- Estatísticas gerais
- Análise de concentração por cedente/sacado
- Cálculo de prazos médios
- Índices de inadimplência

## Controle de Processamento

O sistema mantém um arquivo `processed_folders.json` que registra as pastas já processadas, evitando reprocessamento desnecessário.

## Customização

- Modifique a lista `ignore_list` em ProcessadorPastas para ignorar pastas específicas
- Ajuste os parâmetros de cálculo nas classes ProcessarDados e ProcessarMetricas
- Adicione novos cálculos e métricas conforme necessário

## Contribuições

Apenas os membros especializados da empresa têm autorização para contribuir

## Notas

- Certifique-se de que os arquivos de dados estão no formato esperado
- Verifique a documentação das classes individuais para mais detalhes sobre os cálculos
- Mantenha backup dos dados originais antes do processamento


# Automação de Download - FIDC Midian
script downloader.py
Este script automatiza o processo de download de relatórios de posição do FIDC Midian através do portal FSEngine.

## Funcionalidades

- Login automático no portal FSEngine
- Navegação até a seção de relatórios do FIDC Midian
- Download automático dos relatórios de posição
- Organização dos arquivos por data em pastas específicas
- Controle de relatórios já baixados para evitar duplicidade
- Suporte para arquivos ZIP e CSV
- Processamento em lote de múltiplas páginas de relatórios

## Requisitos

- Python 3.6+
- Selenium WebDriver
- Google Chrome
- ChromeDriver compatível com sua versão do Chrome

## Dependências

```bash
pip install selenium
```

## Estrutura de Arquivos

```
.
            algum diretorio ├── script.py
 downloads/
    ├── processed_dates.txt
    └── YYYY-MM-DD/
        └── arquivos_extraidos
```

## Configuração

1. Instale as dependências necessárias
2. Certifique-se de que o ChromeDriver está instalado e acessível
3. Configure as credenciais de acesso no script:
   ```python
   username_field.send_keys("seu_email@exemplo.com")
   password_field.send_keys("sua_senha")
   ```

## Uso

Execute o script:
O script irá:
1. Criar uma pasta "downloads" no diretório atual (se não existir)
2. Fazer login no portal
3. Navegar até a seção de relatórios
4. Baixar os relatórios não processados anteriormente
5. Organizar os arquivos em pastas por data

## Controle de Downloads

O script mantém um arquivo `processed_dates.txt` que registra as datas dos relatórios já processados, evitando downloads duplicados em execuções futuras.

## Customização

- Altere `min_page` para definir até qual página o script deve retroceder
- Descomente a linha `chrome_options.add_argument("--headless")` para executar em modo headless
- Modifique `downloads_base` para alterar o diretório de download

## Tratamento de Erros

O script inclui:
- Espera dinâmica por elementos da página
- Tratamento de diferentes formatos de arquivo (ZIP/CSV)
- Verificação de downloads completos
- Logging de operações e erros

## Notas de Segurança

- Não armazenar credenciais diretamente no código, como login e senha
- Considere usar variáveis de ambiente ou arquivo de configuração separado para credenciais

## Limitações

- Funciona apenas com o Google Chrome
- Requer conexão estável com a internet
- Específico para a estrutura atual do portal FSEngine


# Classes
## ProcessadorPastas

`ProcessadorPastas` é uma classe para gerenciar diretórios que seguem o padrão de nomenclatura `YYYY-MM-DD`, identificando automaticamente a pasta de dados (`Data`) e listando arquivos `.csv` organizados por data.

### Funcionalidades
- **Busca automática da pasta `Data`** no diretório do projeto.
- **Filtra e ordena pastas** pelo formato `YYYY-MM-DD`.
- **Lista arquivos `.csv`** contidos nas subpastas.
- **Identifica a pasta mais recente** com nome padronizado.

### Instalação e Dependências
A classe utiliza módulos padrão do Python, sem necessidade de instalação de pacotes externos.

### Uso

```python
# iniclz a classe autmtc buscando a pasta 'data'
processador = ProcessadorPastas()
#

# exibe a lista de arqvs csv
print(processador.list_files)
#

# exibe a lista de pasts valds ordnds por data
print(processador.valid_folders)


# obthm a pasta mais recnte disponivel
print(processador.latest_folder)
```
### Métodos Principais

- **`encontrar_data()`** → Procura pela pasta `Data` no diretório do projeto.
- **`nome_pasta_valido(nome_pasta)`** → Verifica se o nome da pasta segue o formato `YYYY-MM-DD`.
- **`obter_pastas_validas()`** → Retorna a lista de pastas ordenadas por data.
- **`obter_ultima_pasta()`** → Retorna a pasta mais recente.

### Observações
- Caso a pasta `Data` não seja encontrada, a classe emite um aviso e não processa arquivos.
- Arquivos `.csv` são considerados apenas se estiverem dentro de subpastas com nomes no formato correto.

### Métodos Principais

- **`encontrar_data()`** → Procura pela pasta `Data` no diretório do projeto.
- **`nome_pasta_valido(nome_pasta)`** → Verifica se o nome da pasta segue o formato `YYYY-MM-DD`.
- **`obter_pastas_validas()`** → Retorna a lista de pastas ordenadas por data.
- **`obter_ultima_pasta()`** → Retorna a pasta mais recente.

## Classe ImportadorDados

`ImportadorDados` é responsável por localizar e carregar um arquivo de feriados automaticamente no repositório, além de importar grandes volumes de dados otimizando memória e desempenho.

### Funcionalidades
- **Busca o arquivo de feriados nacionais** no repositório de forma automática.
- **Carrega e processa feriados**, removendo valores inválidos.
- **Define datas de referência** para seleção de estoque.
- **Importa e otimiza a leitura de arquivos CSV grandes**, convertendo e ajustando tipos de dados.

### Uso

```python
#from importador_dados import ImportadorDados
importador = ImportadorDados()
print("Feriados carregados:", importador.holidays)
print("Data de referência:", importador.ref_date)
print("Último dia útil do mês anterior:", importador.eom_date)
df_final = importador.importar_dados(processador_pastas.list_files)
```
### Métodos Principais

- **`encontrar_repo_root()`** → Identifica o diretório raiz do repositório.
- **`encontrar_arquivo_feriados()`** → Busca automaticamente pelo arquivo de feriados no repositório.
- **`carregar_feriados()`** → Lê o arquivo de feriados e remove dados inválidos.
- **`definir_datas_referencia()`** → Define as datas de referência e o último dia útil do mês anterior.
- **`importar_dados(list_files)`** → Processa arquivos CSV grandes de forma otimizada.

## Melhorias no Processamento de Dados
- **Menos consumo de memória** → Processamento em chunks evita carregamento de arquivos gigantes.
- **Conversão de dados otimizada** → Uso de métodos vetorizados para acelerar a conversão.
- **Descarte imediato de colunas desnecessárias** → Liberação de memória durante o processamento.
- **Validação distribuída** → Os dados são validados por partes, evitando erros acumulados.
- **Menos impacto de impressão** → Redução de mensagens desnecessárias para agilizar a execução.

| **Classe**             | **Função**                               | **Tipo de Retorno**                    | **Descrição Resumida**                                                                                                                   |
|------------------------|------------------------------------------|----------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| **ProcessarMetricas**  | `adicionar_colunas()`                    | `pd.DataFrame`                         | Adiciona colunas calculadas ao *DataFrame* (por ex. prazos e valor líquido atual) e retorna o próprio *DataFrame*.                       |
| **ProcessarMetricas**  | `calcular_metricas()`                    | `dict`                                 | Calcula diversas métricas financeiras (concentração por cedente, índice de inadimplência, etc.) e as retorna em um dicionário.           |
| **ProcessarMetricas**  | `calcular_estatisticas()`                | `dict`                                 | Calcula estatísticas diversas (máximos, contagens, etc.) e retorna um dicionário com esses valores.                                       |
| **ProcessarMetricas**  | `concentracao_por_cedente_sacado()`      | `dict`                                 | Retorna um dicionário com duas *Series*, indicando a concentração de “Valor Atual” por cedente e por sacado.                             |
| **ProcessarMetricas**  | `prazo_medio_ponderado()`                | `float` ou `None`                      | Calcula o prazo médio ponderado (dias até vencimento) com base em “Valor Atual”; pode retornar `None` se colunas não existirem.          |
| **ProcessarMetricas**  | `indice_inadimplencia()`                 | `float` ou `None`                      | Calcula o índice de inadimplência em relação ao “Valor Atual”; pode retornar `None` se colunas necessárias não existirem.                |
| **ProcessarMetricas**  | `taxa_media()`                           | `float` ou `None`                      | Retorna a taxa média (ponderada por “Valor Atual”), ou `None` se não houver dados suficientes.                                            |
| **ProcessarMetricas**  | `volume_por_categoria(categoria)`        | `pd.Series` ou `None`                  | Agrupa e soma “Valor Atual” por uma categoria específica. Retorna `None` se a coluna não existir.                                         |
| **ImportadorDados**    | `encontrar_repo_root()`                  | `str`                                  | Retorna o caminho (string) para a raiz do repositório, baseado em busca ascendente de diretórios.                                         |
| **ImportadorDados**    | `encontrar_arquivo_feriados()`           | `str` ou `None`                        | Retorna o caminho completo do arquivo de feriados, se encontrado, ou `None` caso contrário.                                              |
| **ImportadorDados**    | `carregar_feriados()`                    | `list` *(de datas)*                   | Lê o arquivo de feriados em Excel e retorna uma lista de datas (`datetime`).                                                             |
| **ImportadorDados**    | `definir_datas_referencia()`             | `None`                                 | Define datas de referência (`self.ref_date`, `self.eom_date`) internamente; não retorna nada.                                             |
| **ImportadorDados**    | `importar_dados(list_files)`             | `pd.DataFrame`                         | Lê e processa múltiplos arquivos CSV, aplicando conversões de tipos e unificando em um único *DataFrame*.                                |
| **ProcessarDados**     | `dist_capag(class_col, col_valor)`       | `pd.Series`                            | Retorna a distribuição de valores (somatório) por classificação CAPAG.                                                                    |
| **ProcessarDados**     | `custom_fill2(col1, col2)`               | `list`                                 | Gera uma lista preenchida com valores de `col1` ou, se nulos, aplica regras condicionais com `col2`.                                     |
| **ProcessarDados**     | `vencimento_anual(col_valor, col_vcto)`  | `tuple(pd.Series, pd.Series)`          | Retorna duas *Series*: uma com o valor anual e outra com o acumulado percentual.                                                          |
| **ProcessarDados**     | `concentracao_sacado(...)`               | `dict`                                 | Retorna um dicionário com a soma dos maiores sacados conforme a lista de cortes (`cutoffs`).                                              |
| **ProcessarDados**     | `pagamentos_por_ano()`                   | `pd.Series`                            | Agrupa e soma “Valor Atual” por ano de vencimento, retornando uma *Series*.                                                              |
| **ProcessarDados**     | `fluxo_pagamento(horizonte)`             | `pd.Series`                            | Calcula o fluxo de “Valor Atual” por dia, semana ou mês (conforme parâmetro).                                                            |
| **ProcessarDados**     | `percentual_pdd()`                       | `float`                                | Retorna o percentual de PDD em relação ao valor total.                                                                                    |
| **ProcessarDados**     | `taxa_media()`                           | `float`                                | Retorna a taxa média (ponderada por “Valor Atual”).                                                                                      |
| **ProcessarDados**     | `volume_por_categoria(categoria)`        | `pd.Series`                            | Agrupa e retorna o volume (“Valor Atual”) por categoria específica, em formato de *Series*.                                              |




# Requisitos Gerais: 
### Core Data Processing
pandas==2.1.4
numpy==1.26.2

### Data Visualization
matplotlib==3.8.2
seaborn==0.13.0

### Web Automation
selenium==4.15.2
webdriver-manager==4.0.1

### String Matching
fuzzywuzzy==0.18.0
python-Levenshtein==0.23.0  # Opcional, mas recomendado para melhor performance do fuzzywuzzy

### License
Apache 2.0