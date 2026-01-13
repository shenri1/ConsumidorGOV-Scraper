import time
import json
import os
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

from config import config

class ConsumidorScraper:
    def __init__(self):
        self.driver = self._setup_driver()
        # Carrega histórico para não baixar repetidos
        self.downloaded_files = self._load_state(config.JSON_DOWNLOADS)

    def _setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--log-level=3")
        
        prefs = {
            "download.default_directory": str(config.DOWNLOAD_DIR.absolute()),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        return webdriver.Chrome(options=chrome_options)

    def _load_state(self, path):
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return set(json.load(f))
        return set()

    def _save_state(self, path, data):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(list(data), f, ensure_ascii=False, indent=4)

    def _wait_for_download(self, directory, timeout=60):
        """Espera até que não haja arquivos .crdownload na pasta"""
        end_time = time.time() + timeout
        while time.time() < end_time:
            if not any(f.endswith(".crdownload") for f in os.listdir(directory)):
                return
            time.sleep(1)

    def run(self):
        print("\n--- Iniciando Scraping (Consumidor.gov) ---")
        self.driver.get(config.TARGET_URL)

        # 1. Configuração da Tabela (Lógica Original Restaurada)
        try:
            print("Selecionando visualização de 10 itens...")
            select_n_elements = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.NAME, "publicacoesDT_length"))
            )
            select = Select(select_n_elements)
            select.select_by_value("10")
            
            # Mantendo o sleep original de 40s pois o site demora para renderizar o AJAX
            print("Aguarde 40 segundos para carregamento da tabela...")
            for _ in tqdm(range(40), desc="Carregando site", bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}s'):
                time.sleep(1)
                
        except Exception as e:
            print(f"Erro ao configurar tabela inicial: {e}")
            self.driver.quit()
            return

        # 2. Loop de Paginação e Download
        page_count = 1
        while True:
            print(f"\n--- Processando Página {page_count} ---")
            
            # Chama função que varre a tabela atual
            self._process_current_table()
            
            # Lógica de Paginação (Botão "Próximo")
            try:
                botao_seguinte = self.driver.find_element(By.ID, "publicacoesDT_next")
                classe = botao_seguinte.get_attribute("class")
                
                if "ui-state-disabled" in classe:
                    print("Última página alcançada.")
                    break
                else:
                    botao_seguinte.click()
                    # Pequena pausa para a transição de página
                    time.sleep(5)
                    page_count += 1
            except Exception as e:
                print(f"Erro ao mudar de página ou fim da paginação: {e}")
                break
        
        self.driver.quit()

    def _process_current_table(self):
        """
        Varre as linhas da tabela visível e baixa os arquivos necessários.
        """
        try:
            linhas = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//table[@id='publicacoesDT']/tbody/tr"))
            )
        except Exception as e:
            print(f"Erro ao ler linhas da tabela: {e}")
            return

        # Itera sobre as linhas encontradas
        for linha in linhas:
            try:
                # Pega o nome do arquivo na coluna 2
                nome_elemento = linha.find_element(By.XPATH, "./td[2]")
                texto = nome_elemento.text.strip()
                
                # Verifica critério: Começa com "Dados -"
                if texto.startswith("Dados -"):
                    nome_arquivo = texto
                    
                    if nome_arquivo in self.downloaded_files:
                        continue
                    
                    # Encontra botão e clica
                    botao = linha.find_element(By.XPATH, ".//button[contains(@onclick, 'download')]")
                    botao.click()
                    
                    print(f"> Baixando: {nome_arquivo}")
                    
                    # Espera download efetivar
                    time.sleep(2) # Aguarda inicio
                    self._wait_for_download(config.DOWNLOAD_DIR) # Aguarda fim
                    
                    # Atualiza JSON
                    self.downloaded_files.add(nome_arquivo)
                    self._save_state(config.JSON_DOWNLOADS, self.downloaded_files)
                    
                    # Pausa de segurança entre downloads (do original)
                    time.sleep(3)
                    
            except Exception as e:
                # StaleElementReferenceException pode ocorrer se a página atualizar enquanto lemos
                # Nesse caso, passamos para a próxima iteração
                continue