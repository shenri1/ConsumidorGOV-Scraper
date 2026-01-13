import os
from pathlib import Path

# Diretório Base
BASE_DIR = Path(__file__).resolve().parent.parent / "dados_consumidor_gov"

# Subdiretórios
DOWNLOAD_DIR = BASE_DIR / "downloads"
UNZIP_DIR = BASE_DIR / "descompactados"
OUTPUT_DIR = BASE_DIR / "relatorios"

# Arquivos de Controle de Estado
JSON_DOWNLOADS = BASE_DIR / "historico_downloads.json"
JSON_UNZIPS = BASE_DIR / "historico_descompactados.json"

# URLs e Constantes
TARGET_URL = "https://consumidor.gov.br/pages/dadosabertos/externo/"
TIMEOUT = 20

def setup_directories():
    """Cria a estrutura de pastas se não existir."""
    for directory in [DOWNLOAD_DIR, UNZIP_DIR, OUTPUT_DIR]:
        directory.mkdir(parents=True, exist_ok=True)