import os
import sys

# Garantir que a pasta raiz do projeto está no PATH para importações corretas
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from pipeline.extract import extract_football_data, extract_fbref
from pipeline.transform import merge_sources, compute_pipeline_features
from pipeline.load import append_new_matches

# Configurações globais
TARGET_FILE = os.path.join(ROOT_DIR, "Datasets", "dataset_final_merged_v2.csv")
SEASONS_TO_PROCESS = ["2425", "2526"]  # Épocas Alvo

def run_pipeline():
    print("=" * 60)
    print("INICIANDO O PIPELINE AUTOMÁTICO DE ATUALIZAÇÃO DE DADOS")
    print("=" * 60)
    print(f"Ficheiro de destino configurado: {TARGET_FILE}\n")
    
    for season in SEASONS_TO_PROCESS:
        formatted_season = f"20{season[0:2]}/20{season[2:4]}"
        print(f"\n--- [Pipeline] Processando Época {formatted_season} ---")
        
        # Passo 1: Extração
        df_fd = extract_football_data(season)
        df_fb = extract_fbref(season)  # De momento retorna None (esqueleto)
        
        if df_fd is None:
            print(f"[Pipeline] Avançando Época {formatted_season} devido a erro na extração.")
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
