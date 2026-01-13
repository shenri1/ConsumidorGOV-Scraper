from config import config
from scraper.scraper import ConsumidorScraper
from etl.etl import DataProcessor

def get_user_inputs():
    print("\n" + "="*50)
    print("CONFIGURAÇÃO DE PESQUISA")
    print("="*50)
    
    # 1. Coleta Empresas
    print("\n--- Filtro 1: Empresas ---")
    print("Digite os nomes (ex: Equatorial, Banco do Brasil)")
    input_emp = input("Empresas: ")
    companies = [c.strip() for c in input_emp.split(',') if c.strip()]
    
    # 2. Coleta Segmentos
    print("\n--- Filtro 2: Segmentos de Mercado ---")
    print("Digite os segmentos (ex: Energia Elétrica, Bancos, Aviação)")
    input_seg = input("Segmentos: ")
    segments = [s.strip() for s in input_seg.split(',') if s.strip()]

    # Feedback visual
    print("-" * 30)
    print(f"Empresas alvo : {companies if companies else '(Nenhuma)'}")
    print(f"Segmentos alvo: {segments if segments else '(Nenhum)'}")
    print("-" * 30)
    
    return companies, segments

def main():
    # 1. Input do Usuário
    target_companies, target_segments = get_user_inputs()

    # 2. Preparar ambiente
    config.setup_directories()
    
    # 3. Executar Download
    scraper = ConsumidorScraper()
    scraper.run()
    
    # 4. Executar ETL
    processor = DataProcessor()
    processor.unzip_new_files()
    
    processor.process_csvs(target_companies, target_segments)
    
    print("\n" + "="*50)
    print(f"Execução finalizada. Verifique a pasta: {config.OUTPUT_DIR}")

if __name__ == "__main__":
    main()