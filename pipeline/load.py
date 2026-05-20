import os
import pandas as pd
import numpy as np

def calculate_rolling_features(df, window=5):
    """
    Recalcula as rolling features (médias móveis de 5 jogos) de forma contínua
    em todo o histórico para evitar data leakage e garantir consistência perfeita.
    """
    print(f"[Load] A calcular as rolling features de forma (médias móveis com Janela={window})...")
    df = df.copy()
    
    # Garantir datetime e ordenação temporal absoluta
    df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
    df = df.dropna(subset=['Data']).sort_values('Data').reset_index(drop=True)
    
    # Criar tabela auxiliar de resultados por equipa (Casa e Visitante misturados)
    home_games = df[['Data', 'Equipa_Casa', 'Golos_Casa_Final', 'Golos_Visitante_Final', 'Resultado_Final']].rename(
        columns={'Equipa_Casa': 'Team', 'Golos_Casa_Final': 'GF', 'Golos_Visitante_Final': 'GA', 'Resultado_Final': 'Res'}
    )
    home_games['Pts'] = home_games['Res'].map({'H': 3, 'D': 1, 'A': 0})
    home_games['Venue'] = 'Home'
    home_games['MatchID'] = df.index  # Referência ao jogo original

    away_games = df[['Data', 'Equipa_Visitante', 'Golos_Visitante_Final', 'Golos_Casa_Final', 'Resultado_Final']].rename(
        columns={'Equipa_Visitante': 'Team', 'Golos_Visitante_Final': 'GF', 'Golos_Casa_Final': 'GA', 'Resultado_Final': 'Res'}
    )
    away_games['Pts'] = away_games['Res'].map({'A': 3, 'D': 1, 'H': 0})
    away_games['Venue'] = 'Away'
    away_games['MatchID'] = df.index

    # Stacking temporal
    team_stats = pd.concat([home_games, away_games]).sort_values(['Team', 'Data'])
    
    # SHIFT(1) É CRÍTICO: Para o jogo de hoje, usa-se a forma dos 5 jogos anteriores!
    team_stats['Form_Pts'] = team_stats.groupby('Team')['Pts'].transform(
        lambda x: x.shift(1).rolling(window=window, min_periods=1).sum().fillna(0)
    )
    team_stats['Form_GM'] = team_stats.groupby('Team')['GF'].transform(
        lambda x: x.shift(1).rolling(window=window, min_periods=1).mean().fillna(0)
    )
    team_stats['Form_GS'] = team_stats.groupby('Team')['GA'].transform(
        lambda x: x.shift(1).rolling(window=window, min_periods=1).mean().fillna(0)
    )

    team_stats['IsDraw'] = (team_stats['Res'] == 'D').astype(int)
    team_stats['Form_Empates'] = team_stats.groupby('Team')['IsDraw'].transform(
        lambda x: x.shift(1).rolling(window=window, min_periods=1).sum().fillna(0)
    )

    # Separar Casa e Fora
    stats_home = team_stats[team_stats['Venue'] == 'Home'].set_index('MatchID')[['Form_Pts', 'Form_GM', 'Form_GS', 'Form_Empates']]
    stats_home.columns = [f'Casa_{c}{window}' for c in stats_home.columns]
    
    stats_away = team_stats[team_stats['Venue'] == 'Away'].set_index('MatchID')[['Form_Pts', 'Form_GM', 'Form_GS', 'Form_Empates']]
    stats_away.columns = [f'Visitante_{c}{window}' for c in stats_away.columns]
    
    # Dropar colunas antigas de rolling features para evitar duplicados
    cols_to_drop = list(stats_home.columns) + list(stats_away.columns)
    df_clean = df.drop(columns=[c for c in cols_to_drop if c in df.columns], errors='ignore')
    
    # Merge de volta
    df_enriched = df_clean.join(stats_home).join(stats_away)
    return df_enriched

def append_new_matches(df_new, target_file_path):
    """
    Carrega o dataset histórico existente, identifica novos jogos (com data superior
    ao jogo mais recente no histórico), anexa-os de forma idempotente e recalcula
    as rolling features antes de salvar na codificação Latin-1.
    """
    print(f"[Load] A iniciar processo de gravação para: {target_file_path}")
    
    if df_new is None or df_new.empty:
        print("[Load] Aviso: Sem novos dados para carregar.")
        return False
        
    # Se o ficheiro ainda não existir, inicializa de raiz
    if not os.path.exists(target_file_path):
        print(f"[Load] Ficheiro destino não existe. A criar novo em {target_file_path}")
        df_new_enriched = calculate_rolling_features(df_new)
        df_new_enriched.to_csv(target_file_path, index=False, encoding='latin1')
        return True
        
    try:
        # Carregar dataset histórico usando latin1
        df_existing = pd.read_csv(target_file_path, low_memory=False, encoding='latin1')
        
        # Assegurar formato datetime
        df_existing['Data'] = pd.to_datetime(df_existing['Data'], errors='coerce')
        df_new['Data'] = pd.to_datetime(df_new['Data'], errors='coerce')
        
        # Determinar a data do jogo mais recente no histórico
        max_date_existing = df_existing['Data'].max()
        print(f"[Load] Data do jogo mais recente no histórico: {max_date_existing}")
        
        # Filtrar apenas os jogos posteriores a essa data
        df_to_append = df_new[df_new['Data'] > max_date_existing]
        
        if df_to_append.empty:
            print("[Load] Tudo atualizado! Não há novos jogos para anexar.")
            return True
            
        print(f"[Load] Encontrados {len(df_to_append)} novos jogos para anexar.")
        
        # Concatenar dados novos e antigos
        df_final = pd.concat([df_existing, df_to_append], ignore_index=True)
        
        # Recalcular as médias móveis em todo o histórico combinado
        df_final_enriched = calculate_rolling_features(df_final)
        
        # Re-ordenar temporalmente e restaurar formato de string de data se desejado,
        # ou gravar diretamente como datetime (pandas grava no formato YYYY-MM-DD)
        df_final_enriched = df_final_enriched.sort_values('Data').reset_index(drop=True)
        
        # Gravar de volta em Latin-1
        df_final_enriched.to_csv(target_file_path, index=False, encoding='latin1')
        print(f"[Load] Sucesso! Dataset atualizado e guardado com {len(df_final_enriched)} linhas totais.")
        return True
        
    except Exception as e:
        print(f"[Load] Erro fatal durante a gravação: {e}")
        return False

if __name__ == "__main__":
    print("Script de Carregamento (Load) ativo.")
