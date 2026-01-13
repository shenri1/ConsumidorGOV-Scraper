# 📊 ConsumidorGOV-Scraper

Ferramenta automatizada para extração, processamento e análise de dados públicos do portal **Consumidor.gov.br**.

O script realiza o download automático dos arquivos `.zip` mensais, descompacta, processa os arquivos `.csv` gigantes e gera relatórios Excel filtrados por **Empresas** e **Segmentos de Mercado** definidos pelo usuário.

## 🚀 Funcionalidades

* **Scraping Automático:** Navega, espera o carregamento (AJAX) e baixa novos arquivos automaticamente via Selenium.
* **Controle de Estado:** Mantém histórico (`.json`) para não baixar ou descompactar arquivos repetidos.
* **Filtros Dinâmicos:** O usuário define quais empresas e segmentos deseja extrair.
* **Barra de Progresso:** Visualização do andamento (tqdm) para downloads e processamento de dados.
* **Estrutura Modular:** Código organizado em módulos de configuração, extração e transformação.

## 📋 Pré-requisitos

* Python 3.8 ou superior.
* Google Chrome instalado (em breve para Firefox).

## 🛠️ Instalação

1. Clone ou baixe este repositório.
2. Instale as dependências necessárias via terminal:

```bash
pip install requirements.txt

```

## 📂 Estrutura do Projeto

Certifique-se de que sua pasta esteja organizada desta forma:

```text
PROJETO_RAIZ/
│
├── main.py                  # Arquivo principal (Executar este)
│
├── config/
│   ├── __init__.py
│   └── config.py            # Configurações de diretórios
│
├── scraper/
│   ├── __init__.py
│   └── scraper.py           # Automação Web (Selenium)
│
└── etl/
    ├── __init__.py
    └── etl.py               # Processamento de dados (Pandas)

```

## ▶️ Como Usar

1. Abra o terminal na pasta do projeto.
2. Execute o script principal:

```
python main.py

```

3. **Siga as instruções no terminal:**

* Digite os nomes das **Empresas** que deseja filtrar (ex: `Equatorial, Banco do Brasil`).
* Digite os **Segmentos** que deseja filtrar (ex: `Energia Elétrica, Bancos`).

4. **Aguarde o Processamento:**

* O script abrirá o navegador em modo oculto (*headless*).
* Haverá uma espera de **40 segundos** (barra de progresso visível) para o carregamento da tabela do site do governo.
* Os arquivos serão baixados na pasta `downloads/` e extraídos em `descompactados/`.

## 📤 Resultados

Os relatórios finais serão salvos automaticamente na pasta:
`dados_consumidor_gov/relatorios/`

* **`dados_empresas_NomeDaEmpresa.xlsx`**: Contém todas as reclamações das empresas solicitadas.
* **`dados_segmento_NomeDoSegmento.xlsx`**: Contém todas as reclamações do segmento de mercado solicitado.

---

**Nota:** O site *consumidor.gov.br* possui um carregamento lento via AJAX. O script foi configurado para respeitar esse tempo (40s) para garantir que todos os dados sejam capturados corretamente.
