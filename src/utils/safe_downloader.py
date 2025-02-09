####
####                ATENÇÃO  !!! 
####                Abaixo você tem que logar o LOGIN e SENHA no seu Computador 
####                onde estiver "NOME DO FUNDO" você irá substituir pelo nome do fundo 
####                que você precisa baixar,  deve aparecer como algo do tipo
####                mezanino-asset , ou algo desse tipo
####      dúvidas: lucas_r_andrade@hotmail.com
import os  # Custos viarum
import time  # Dominus temporis
import zipfile  # Artifex compressionis
import shutil  # Magister mutationis
from datetime import datetime  # Computator horarum
from urllib.parse import urlparse, parse_qs  # Interpres chartarum digitalium
##==##==##==##==##==##==##==##==##==##==##==##==##==##==##==##==##==##==##==##==##==
from selenium import webdriver  # Viator indefessus
from selenium.webdriver.common.by import By  # Explorator vigilans
from selenium.webdriver.chrome.service import Service as ChromeService  # Machinator occultus
from selenium.webdriver.support.ui import WebDriverWait  # Sapiens patiens
from selenium.webdriver.support import expected_conditions as EC  # Oraculum interretiale
#  ||         ||         ||            ||     ||         ||           ||       ||   || |||
# || ||   ||   ||||            ||             |||            |                   |       ||
def wait_for_download_indefinitely(download_dir, old_files):
    """
    Esta máquina apenas pega 2G :( :( 
    Na certeza da 5G daria para ter abordagens mais rápidas, mas esse código roda mesmo ans piores internets 
    Aqui eu vou fazer ele esperar o quanto for necessário até que o download seja concluído
    Como eu sei? eu vejo se ele tá dizendo que o nome do arquivo é um donwload nao confirmado, 
    Se for ele continua esperando
    Minha ideia aqui é garantir que antes de ele iniciar o próximo download, ele garanta que o 
    anterior foi baixado e descompactado
    """
    print("Aguardando conclusão do download...")
    while True:
        current_files = set(os.listdir(download_dir))
        new_files = current_files - old_files
        # Filtra arquivos temporários (ex.: .crdownload)
        finished_files = [f for f in new_files if not f.endswith(".crdownload")]
        if finished_files:
            return finished_files[0]
        time.sleep(1)

def process_downloaded_file(download_dir, file_name, folder_date):
    """
    Se o arquivo baixado for ZIP, extrai-o para a pasta download_dir/folder_date;
    se for CSV, move o arquivo para essa pasta.
    pq eu fiz isso? simples, porque eu posso adaptar essa main para baixar outros arquivos da 
    FS engine 
    """
    dest_folder = os.path.join(download_dir, folder_date)
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    
    file_path = os.path.join(download_dir, file_name)
    if file_name.lower().endswith(".zip"):
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(dest_folder)
        print(f"Arquivo ZIP extraído para {dest_folder}")
        os.remove(file_path)  # remove o ZIP, pra n ocupar tnt memoria
    elif file_name.lower().endswith(".csv"):
        shutil.move(file_path, os.path.join(dest_folder, file_name))
        print(f"Arquivo CSV movido para {dest_folder}")
    else:
        print(f"Arquivo {file_name} não é CSV nem ZIP.")

def load_processed_dates(processed_file_path):
    """Lê o arquivo de datas processadas e retorna um conjunto, para saber quais datas já foram 
    baixadas, assim ele evita de re-biaxar td de novo"""
    if os.path.exists(processed_file_path):
        with open(processed_file_path, "r", encoding="utf-8") as f:
            dates = {line.strip() for line in f if line.strip()}
        return dates
    return set()

def update_processed_dates(processed_file_path, processed_dates):
    """Atualiza o file kas datas processadas.
    de novo para ganhar escala, pra pode rusar outras linhas da tabela do FS engine    """
    with open(processed_file_path, "w", encoding="utf-8") as f:
        for d in sorted(processed_dates):
            f.write(f"{d}\n")

def get_last_page(driver):
    """
    Obtém o número da última página a partir do link com title "Última Página".
    Caso não encontre, retorna o maior número dentre os links numéricos.
    Atualmente está em 10 (Fevereiro de 2025), mas eu aposto que esse numero vai subir
    """
    try:
        ultima = driver.find_element(By.XPATH, "//li[@title='Última Página']/a")
        ultima_href = ultima.get_attribute("href")
        # Exemplo de href: "?page=10&amp;"
        parsed = urlparse(ultima_href)
        params = parse_qs(parsed.query)
        last_page = int(params.get("page", [1])[0])
        return last_page
    except Exception as e:
        # Se não conseguir, tenta obter o maior número dos links visíveis
        page_numbers = []
        for a in driver.find_elements(By.CSS_SELECTOR, "ul.pagination li a.page-link"):
            try:
                num = int(a.text.strip())
                page_numbers.append(num)
            except:
                pass
        return max(page_numbers) if page_numbers else 1

def main():
    base_url = "https://fsengine.com.br"
    downloads_base = os.path.join(os.getcwd(), "downloads")
    if not os.path.exists(downloads_base): # aqui vai criar uma pasta s eja nao tiver
        os.makedirs(downloads_base)
        print(f"Pasta de download criada: {downloads_base}")
    else:
        print(f"Pasta de download existente: {downloads_base}")
    
    #### vamos ler um txt para ver o que ja foi salvo #################
    processed_file = os.path.join(downloads_base, "processed_dates.txt")
    processed_dates = load_processed_dates(processed_file)
    print("Datas já processadas:", processed_dates)
    ### aqui eu estou usando o Chrome, meu navegador preferido, até pq eu suponho que de para usar o Colab com isso ########
    chrome_options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": downloads_base, ###aqui ele tem essa incrivel opção de selecionar onde baixar
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    # aqui eu estou mostrando tudo IRT para que o usuário possa ver o que está acontecendo. Porém, s enão 
    #quiser,  pode codar o que está abaixo e então ele vai fazer automaticamente
    # chrome_options.add_argument("--headless") # comente isso para mostrar o navegador trabalhando
    
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 20)
    
    try:
        # ===##==##==##==##==##=    1. LOGIN E NAVEGAÇÃO INICIAL ===##==##==##==##==##==##==##==##
        driver.get(f"{base_url}/fundos/")
        print("Página de login aberta.")
        
        #####################        CAUTION   ATENÇÂO              ###############################
        ## Não compartilhe!!!!             Do NOT Share this info ##            
        username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        password_field = wait.until(EC.presence_of_element_located((By.NAME, "password")))
        username_field.send_keys("INSIRA SEU LOGIN AQUI-- INSERT LOGIN ")
        password_field.send_keys("INSIRA SUA SENHA AQUI  --INSERT PASSWORD ")
        
        login_button = driver.find_element(By.CSS_SELECTOR, "button.btn.btn-brand-02.btn-block")
        login_button.click()
        print("Login efetuado.")
        
        # INSIRA AQUI ABAIXO  O NOME DO FUNDO 
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "a.card.card-body.p-3.mb-1.tx-black[href='/fundos/NOME DO FUNDO/']")
        ))
        print("Página pós-login carregada.")
        
        # Clica no card "NOME DO FUNDO"
        fundo_card = driver.find_element( ##OBSERVAÇÂO:aqui pode adicionar mais fundos, estou supondo que só um ja seja suficiente
            By.CSS_SELECTOR, 
            "a.card.card-body.p-3.mb-1.tx-black[href='/fundos/NOME DO FUNDO/']"
        )
        fundo_card.click()
        print("Card 'NOME DO FUNDO' clicado.")
        
        # espera a pgin interna do fundo e clic na aba "Relatórios"
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "a.btn.btn-sm.pd-x-15.btn-uppercase.btn-white[href='/fundos/NOME DO FUNDO/relatorios/']")
        ))
        relatorios_tab = driver.find_element(
            By.CSS_SELECTOR, 
            "a.btn.btn-sm.pd-x-15.btn-uppercase.btn-white[href='/fundos/NOME DO FUNDO/relatorios/']"
        )
        relatorios_tab.click()
        print("Aba 'Relatórios' acessada.")
        
        # Aguarda a barra dos numerozinhos 
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.pagination")))
        print("Barra de paginação carregada.")
        
        # --- Obter o número da última página ---
        last_page = get_last_page(driver)
        print(f"Número da última página encontrado: {last_page}")
        # Defina a pg min a ser processada; aq até a página 8
        min_page = 8
        if last_page < min_page:     ## sendo soh um pqnho paranoico
            min_page = 1
        
        # ===##==##==##==##==##=    2. ITERA DAS PÁGINAS DA ÚLTIMA ATÉ A (min_page)    # ===##==##==##==##==##= 
        # Claro, tu pode deixar ateh a primeia   recomendo comecao pro minpage =8 
        for page in range(last_page, min_page - 1, -1):
            list_page_url = f"{base_url}/fundos/NOME DO FUNDO/relatorios/?page={page}&"
            driver.get(list_page_url)
            print(f"\nNavegando para a página {page} ...")
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.list-group")))
            time.sleep(2)  # Aguarda a lista carregar
            
            # Coleta todos os elementos da lista de relatórios
            report_elements = driver.find_elements(
                By.XPATH, "//div[@class='list-group']/a[contains(@class, 'list-group-item')]"
            )
            
            # Cria uma lista de relatórios a processar: tupla (href, folder_date)
            reports_to_process = []
            for elem in report_elements:
                try:
                    row = elem.find_element(By.XPATH, ".//div[@class='row']")
                    columns = row.find_elements(By.XPATH, "./div")
                    if len(columns) >= 2:
                        # Agora o filtro é: coluna 1 contém "Posição" e coluna 2 contém "Fechamento de"
                        tipo = columns[0].text.strip()
                        detalhes = columns[1].text.strip()
                        if "Posição" in tipo and "Fechamento de" in detalhes:
                            # Extrai a data removendo o prefixo "Fechamento de"   #podia subs por abertura tbm
                            date_str = detalhes.replace("Fechamento de", "").strip()
                            try:
                                folder_date = datetime.strptime(date_str, "%d/%m/%y").strftime("%Y-%m-%d")
                            except Exception as parse_ex:
                                print(f"Erro ao converter data '{date_str}':", parse_ex)
                                continue
                            
                            # Se essa data já foi salva, ignora
                            if folder_date in processed_dates:
                                print(f"Relatório com data {folder_date} já processado. Ignorando.")
                            else:
                                href = elem.get_attribute("href")
                                if not href.startswith("http"):
                                    href = base_url + href
                                reports_to_process.append((href, folder_date))
                except Exception as ex:
                    print("Erro ao processar um elemento da lista:", ex)
            
            print(f"Na página {page} foram encontrados {len(reports_to_process)} relatórios a processar.")
            
            ## ===##==##==##==##==##=    3. PROCESSA CADA RELATÓRIO NA PÁGINA     # ===##==##==##==##==##=   
            for idx, (report_href, folder_date) in enumerate(reports_to_process, start=1):
                print(f"\nProcessando relatório {idx} da página {page}: {report_href} com data {folder_date}")
                driver.get(report_href)
                
                # Aguarda o botão "Baixar"
                download_button = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//a[contains(@class, 'btn-primary') and contains(normalize-space(.), 'Baixar')]")
                ))
                # Regist os arqvs existentes antes do dwnld
                old_files = set(os.listdir(downloads_base))
                
                driver.execute_script("arguments[0].scrollIntoView(true);", download_button)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", download_button)
                print("Botão 'Baixar' clicado. Aguardando download...")
                
                downloaded_file = wait_for_download_indefinitely(downloads_base, old_files)
                print(f"Arquivo baixado: {downloaded_file}")
                process_downloaded_file(downloads_base, downloaded_file, folder_date)
                
                # Add a date processada e atualiza o txt que salva oq já foi baixado
                processed_dates.add(folder_date)
                update_processed_dates(processed_file, processed_dates)
                
                # dps do download, clic no botão "Voltar" p/ retornar à lista
                voltar_button = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//a[contains(@class, 'btn-secondary') and contains(text(), 'Voltar')]")
                ))
                driver.execute_script("arguments[0].scrollIntoView(true);", voltar_button)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", voltar_button)
                print("Botão 'Voltar' clicado. Retornando à lista...")
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.list-group")))
                time.sleep(2)
        
        print("\nProcessamento de todos os relatórios concluído.")
        
    except Exception as e:
        print("Ocorreu um erro:", e)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
