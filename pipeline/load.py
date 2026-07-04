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
    Carrega o dataset histórico existente, atualiza os resultados dos jogos pre-carregados
    (que estavam como NaN/futuros) e anexa novos jogos posteriores, recalculando as rolling features.
    """
    print(f"[Load] A iniciar processo de atualizacao/gravacao para: {target_file_path}")
    
    if df_new is None or df_new.empty:
        print("[Load] Aviso: Sem novos dados para carregar.")
        return False
        
    # Se o ficheiro ainda não existir, inicializa de raiz
    if not os.path.exists(target_file_path):
        print(f"[Load] Ficheiro destino nao existe. A criar novo em {target_file_path}")
        df_new_enriched = calculate_rolling_features(df_new)
        df_new_enriched.to_csv(target_file_path, index=False, encoding='latin1')
        return True
        
    try:
        # Carregar dataset histórico usando latin1
        df_existing = pd.read_csv(target_file_path, low_memory=False, encoding='latin1')
        
        # Assegurar formato datetime e strings
        df_existing['Data'] = pd.to_datetime(df_existing['Data'], errors='coerce')
        df_new['Data'] = pd.to_datetime(df_new['Data'], errors='coerce')
        
        df_existing['Equipa_Casa'] = df_existing['Equipa_Casa'].astype(str).str.strip()
        df_existing['Equipa_Visitante'] = df_existing['Equipa_Visitante'].astype(str).str.strip()
        df_new['Equipa_Casa'] = df_new['Equipa_Casa'].astype(str).str.strip()
        df_new['Equipa_Visitante'] = df_new['Equipa_Visitante'].astype(str).str.strip()

        # 1. Atualizar jogos existentes que estavam sem resultado (NaN) e agora têm resultado
        updated_count = 0
        
        # Criar chaves únicas temporárias baseadas na Época e equipas (já que cada confronto só acontece uma vez por época em casa)
        df_existing['match_key'] = df_existing['Epoca'].astype(str) + "_" + df_existing['Equipa_Casa'] + "_" + df_existing['Equipa_Visitante']
        df_new['match_key'] = df_new['Epoca'].astype(str) + "_" + df_new['Equipa_Casa'] + "_" + df_new['Equipa_Visitante']
        
        # Filtrar jogos em df_new que têm resultado
        df_new_played = df_new[df_new['Resultado_Final'].notna()]
        
        if not df_new_played.empty:
            new_played_dict = df_new_played.set_index('match_key').to_dict('index')
            
            # Atualizar colunas de resultado e data no df_existing
            cols_to_update = [
                'Data', 'Golos_Casa_Final', 'Golos_Visitante_Final', 'Resultado_Final',
                'Golos_Casa_Intervalo', 'Golos_Visitante_Intervalo', 'Resultado_Intervalo',
                'Remates_Casa', 'Remates_Visitante', 'Remates_Alvo_Casa', 'Remates_Alvo_Visitante',
                'Faltas_Casa', 'Faltas_Visitante', 'Cantos_Casa', 'Cantos_Visitante',
                'Amarelos_Casa', 'Amarelos_Visitante', 'HR', 'AR',
                'Odd_Casa_Bet365', 'Odd_Empate_Bet365', 'Odd_Visitante_Bet365',
                'Odd_Casa_Media', 'Odd_Empate_Media', 'Odd_Visitante_Media'
            ]
            
            for idx, row in df_existing.iterrows():
                key = row['match_key']
                if key in new_played_dict and pd.isna(row['Resultado_Final']):
                    new_val = new_played_dict[key]
                    for col in cols_to_update:
                        if col in new_val and col in df_existing.columns:
                            df_existing.at[idx, col] = new_val[col]
                    updated_count += 1
                    
        # Limpar match_key
        df_existing.drop(columns=['match_key'], inplace=True)
        df_new.drop(columns=['match_key'], inplace=True)
        
        if updated_count > 0:
            print(f"[Load] Atualizados os resultados de {updated_count} jogos pre-existentes.")
            
        # 2. Identificar novos jogos para anexar (com data superior à máxima existente)
        max_date_existing = df_existing['Data'].max()
        df_to_append = df_new[df_new['Data'] > max_date_existing]
        
        has_changes = (updated_count > 0) or (not df_to_append.empty)
        
        if not has_changes:
            print("[Load] Tudo atualizado! Sem novos jogos ou resultados para gravar.")
            return True
            
        if not df_to_append.empty:
            print(f"[Load] Encontrados {len(df_to_append)} novos jogos para anexar.")
            df_final = pd.concat([df_existing, df_to_append], ignore_index=True)
        else:
            df_final = df_existing
            
        # Recalcular as médias móveis em todo o histórico
        df_final_enriched = calculate_rolling_features(df_final)
        df_final_enriched = df_final_enriched.sort_values('Data').reset_index(drop=True)
        
        # Converter coluna de data para string YYYY-MM-DD
        df_final_enriched['Data'] = df_final_enriched['Data'].dt.strftime('%Y-%m-%d')
        
        # Gravar de volta em Latin-1
        df_final_enriched.to_csv(target_file_path, index=False, encoding='latin1')
        print(f"[Load] Sucesso! Dataset atualizado e guardado com {len(df_final_enriched)} linhas totais.")
        return True
        
    except Exception as e:
        print(f"[Load] Erro fatal durante a gravação: {e}")
        return False

if __name__ == "__main__":
    print("Script de Carregamento (Load) ativo.")
