import os
import sys

# Garantir que a pasta raiz do projeto está no PATH para importações corretas
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

import datetime
from pipeline.extract import extract_football_data, extract_fbref
from pipeline.transform import merge_sources, compute_pipeline_features
from pipeline.load import append_new_matches

# Configurações globais
TARGET_FILE = os.path.join(ROOT_DIR, "Datasets", "dataset_final_merged_v2.csv")

def get_seasons_to_process():
    """
    Gera dinamicamente a lista de épocas a processar desde 2024-2025 ('2425')
    até à época atual ou futura em curso.
    """
    seasons = []
    start_year = 2024
    today = datetime.date.today()
    
    # Se for julho ou posterior, o ano de início da época atual é o ano corrente.
    # Caso contrário, é o ano anterior.
    current_season_start_year = today.year if today.month >= 7 else today.year - 1
    
    # Inclui épocas desde a época 2024-2025 até à época atual
    for y in range(start_year, current_season_start_year + 1):
        y1 = str(y)[2:]
        y2 = str(y + 1)[2:]
        seasons.append(f"{y1}{y2}")
        
    # Pre-emptivamente adiciona a próxima época nos meses de transição/verão (Maio e Junho)
    # para garantir suporte imediato assim que os novos calendários/jogos comecem.
    next_year = current_season_start_year + 1
    next_season_str = f"{str(next_year)[2:]}{str(next_year+1)[2:]}"
    if next_season_str not in seasons:
        seasons.append(next_season_str)
        
    return list(sorted(list(set(seasons))))

def run_pipeline():
    print("=" * 60)
    print("INICIANDO O PIPELINE AUTOMÁTICO DE ATUALIZAÇÃO DE DADOS")
    print("=" * 60)
    seasons_to_process = get_seasons_to_process()
    print(f"Épocas identificadas para processamento: {seasons_to_process}\n")
    
    for season in seasons_to_process:
        formatted_season = f"20{season[0:2]}/20{season[2:4]}"
        print(f"\n--- [Pipeline] Processando Época {formatted_season} ---")
        
        # Passo 1: Extração
        df_fd = extract_football_data(season)
        df_fb = extract_fbref(season)  # De momento retorna None (esqueleto)
        
        if df_fd is None or df_fd.empty:
            print(f"[Pipeline] Avançando Época {formatted_season} porque não existem jogos disponíveis ou a época ainda não começou.")
            continue
            
        # Passo 2: Transformação
        df_merged = merge_sources(df_fd, df_fb)
        df_transformed = compute_pipeline_features(df_merged)
        
        if df_transformed is None:
            print(f"[Pipeline] Avançando Época {formatted_season} devido a erro na transformação.")
            continue
            
        # Passo 3: Gravação segura no histórico
        success = append_new_matches(df_transformed, TARGET_FILE)
        
        if success:
            print(f"[Pipeline] Época {formatted_season} processada com sucesso!")
        else:
            print(f"[Pipeline] Erro na gravação da Época {formatted_season}.")
            
    # Passo 4: Atualizar as features avançadas em ambos os ficheiros
    print("\n--- [Pipeline] Iniciando Atualização de Features Avançadas ---")
    try:
        from pipeline.features_avancadas import update_advanced_datasets
        advanced_success = update_advanced_datasets()
        if advanced_success:
            print("[Pipeline] Features avançadas atualizadas com sucesso!")
        else:
            print("[Pipeline] Falha ao atualizar as features avançadas.")
    except Exception as e:
        print(f"[Pipeline] Erro ao importar/executar features avançadas: {e}")
            
    print("\n" + "=" * 60)
    print("PIPELINE DE DADOS CONCLUÍDO COM SUCESSO!")
    print("=" * 60)

if __name__ == "__main__":
    run_pipeline()
