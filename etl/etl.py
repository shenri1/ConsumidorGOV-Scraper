import os
import zipfile
import pandas as pd
import json
import glob
from tqdm import tqdm
from config import config

class DataProcessor:
    def __init__(self):
        self.unzipped_files = self._load_state(config.JSON_UNZIPS)

    def _load_state(self, path):
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return set(json.load(f))
        return set()

    def _save_state(self, path, data):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(list(data), f, ensure_ascii=False, indent=4)

    def unzip_new_files(self):
        print("\n--- Iniciando Descompactação ---")
        zip_files = list(config.DOWNLOAD_DIR.glob('*.zip'))
        
        for zip_path in tqdm(zip_files, desc="Extraindo ZIPs", unit="zip"):
            file_name = zip_path.name
            if file_name in self.unzipped_files:
                continue
            
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(config.UNZIP_DIR)
                self.unzipped_files.add(file_name)
                self._save_state(config.JSON_UNZIPS, self.unzipped_files)
            except zipfile.BadZipFile:
                print(f"Erro: Arquivo corrompido {file_name}")

    def process_csvs(self, target_companies, target_segments):
        """
        Recebe listas de empresas e segmentos para filtrar.
        """
        print("\n--- Iniciando Consolidação de Dados ---")
        csv_files = glob.glob(str(config.UNZIP_DIR / '*.csv'))
        
        dfs = []
        for file in tqdm(csv_files, desc="Lendo CSVs", unit="csv"):
            df = self._read_single_csv(file)
            if df is not None:
                dfs.append(df)
            
            try:
                os.remove(file)
            except OSError:
                pass

        if not dfs:
            print("Nenhum dado novo para processar.")
            return

        print("Concatenando DataFrames...")
        full_df = pd.concat(dfs, ignore_index=True)
        
        # Chama a geração de relatórios passando os dois filtros
        self._generate_reports(full_df, target_companies, target_segments)

    def _read_single_csv(self, file_path):
        for encoding in ['UTF-8', 'ISO-8859-1']:
            try:
                df = pd.read_csv(file_path, encoding=encoding, sep=';')
                # Verificação mínima de colunas
                if 'Nome Fantasia' in df.columns and 'Segmento de Mercado' in df.columns:
                    return df
            except Exception:
                continue
        return None

    def _generate_reports(self, df, target_companies, target_segments):
        print("\nGerando relatórios Excel...")
        
        # 1. Relatório por EMPRESAS (Nome Fantasia)
        if target_companies:
            pattern = '|'.join([c.strip() for c in target_companies if c.strip()])
            mask_companies = df['Nome Fantasia'].str.contains(pattern, case=False, na=False)
            df_companies = df[mask_companies]
            
            name_suffix = '_'.join(target_companies[:2]).replace(' ', '')
            filename = f"dados_empresas_{name_suffix}.xlsx"
            
            self._append_to_excel(df_companies, config.OUTPUT_DIR / filename)
        
        # 2. Relatório por SEGMENTOS (Segmento de Mercado)
        if target_segments:
            pattern_seg = '|'.join([s.strip() for s in target_segments if s.strip()])
            
            # Filtra onde o Segmento OU o Assunto contenha o termo (ex: Energia)
            # Você pode ajustar para filtrar apenas a coluna 'Segmento de Mercado' se preferir, estou pensando se
            # faz sentido incluir o Assunto também.
            mask_segments = (
                df['Segmento de Mercado'].str.contains(pattern_seg, case=False, na=False) |
                df['Assunto'].str.contains(pattern_seg, case=False, na=False)
            )
            df_seg = df[mask_segments]
            
            seg_suffix = '_'.join(target_segments[:2]).replace(' ', '')
            filename_seg = f"dados_segmento_{seg_suffix}.xlsx"
            
            self._append_to_excel(df_seg, config.OUTPUT_DIR / filename_seg)

    def _append_to_excel(self, new_df, file_path):
        if new_df.empty:
            print(f"Aviso: Filtro gerou dados vazios para {file_path.name}")
            return
            
        if file_path.exists():
            old_df = pd.read_excel(file_path)
            combined = pd.concat([old_df, new_df], ignore_index=True)
            combined.drop_duplicates(inplace=True)
        else:
            combined = new_df
        
        combined.to_excel(file_path, index=False)
        print(f"Salvo: {file_path.name} ({len(combined)} registros)")