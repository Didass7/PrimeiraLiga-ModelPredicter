import os
import requests
import pandas as pd

def extract_football_data(season: str):
    """
    Faz o download automático dos dados da Primeira Liga do football-data.co.uk.
    O formato da season deve ser ex: '2425' ou '2526'.
    """
    url = f"https://www.football-data.co.uk/mmz4281/{season}/P1.csv"
    print(f"[Extract] A descarregar dados de Football-Data.co.uk de: {url}")
    try:
        # Pede o CSV diretamente da internet
        df = pd.read_csv(url)
        print(f"[Extract] Download efetuado com sucesso! {len(df)} jogos encontrados.")
        return df
    except Exception as e:
        print(f"[Extract] Erro ao descarregar do Football-Data: {e}")
        return None

def extract_fbref(season: str):
    """
    Esqueleto para o scraper de Selenium do FBRef rodar em modo Headless no GitHub Actions.
    """
    print(f"[Extract] Módulo FBRef ativo para a época {season}.")
    print("[Extract] Dica para GitHub Actions: Configurar o webdriver em modo headless:")
    print("           options = webdriver.ChromeOptions()")
    print("           options.add_argument('--headless')")
    print("           options.add_argument('--no-sandbox')")
    print("           options.add_argument('--disable-dev-shm-usage')")
    
    # Atualmente retorna None até integrarmos os teus seletores de Selenium
    return None

if __name__ == "__main__":
    print("Testando extração do Football-Data para 24/25...")
    df = extract_football_data("2425")
    if df is not None:
        print(df.head(2))
