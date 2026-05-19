import os
import pandas as pd

def append_new_matches(df_new, target_file_path):
    """
    Carrega o dataset histórico existente, identifica novos jogos (com data superior
    ao jogo mais recente no histórico) e faz o append de forma segura sem duplicar dados.
    """
    print(f"[Load] A iniciar processo de gravação para: {target_file_path}")
    
    if df_new is None or df_new.empty:
        print("[Load] Aviso: Sem novos dados para carregar.")
        return False
        
    # Se o ficheiro ainda não existir (segurança), cria um de raiz
    if not os.path.exists(target_file_path):
        print(f"[Load] Ficheiro destino não existe. A criar novo ficheiro em {target_file_path}")
        df_new.to_csv(target_file_path, index=False)
        return True
        
    try:
        # Carregar dataset histórico
        df_existing = pd.read_csv(target_file_path, low_memory=False)
        
        # Assegurar formato datetime
        df_existing['Data'] = pd.to_datetime(df_existing['Data'], errors='coerce')
        df_new['Data'] = pd.to_datetime(df_new['Data'], errors='coerce')
        
        # Determinar a data do jogo mais recente
        max_date_existing = df_existing['Data'].max()
        print(f"[Load] Data do jogo mais recente no histórico: {max_date_existing}")
        
        # Filtrar apenas os jogos posteriores a essa data
        df_to_append = df_new[df_new['Data'] > max_date_existing]
        
        if df_to_append.empty:
            print("[Load] Tudo atualizado! Não há novos jogos para anexar.")
            return True
            
        print(f"[Load] Encontrados {len(df_to_append)} novos jogos para anexar.")
        
        # Concatenar e ordenar temporalmente
        df_final = pd.concat([df_existing, df_to_append], ignore_index=True)
        df_final = df_final.sort_values('Data').reset_index(drop=True)
        
        # Gravar de volta
        df_final.to_csv(target_file_path, index=False)
        print(f"[Load] Sucesso! Dataset atualizado e guardado com {len(df_final)} linhas totais.")
        return True
        
    except Exception as e:
        print(f"[Load] Erro fatal durante a gravação: {e}")
        return False

if __name__ == "__main__":
    print("Script de Carregamento (Load) ativo.")
