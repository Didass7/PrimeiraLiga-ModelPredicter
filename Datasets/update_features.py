import pandas as pd
import numpy as np

# Configuração
INPUT_FILE = r"d:\Diogo\Ambiente de Trabalho\PROJETO\Datasets\dataset_final_merged.csv"
OUTPUT_FILE = r"d:\Diogo\Ambiente de Trabalho\PROJETO\Datasets\dataset_final_merged_v2.csv"
WINDOW = 5

def calculate_rolling_features(df, window=5):
    print("A iniciar cálculo de features de forma...")
    # Garantir datetime
    df['Data'] = pd.to_datetime(df['Data'], dayfirst=True)
    
    # Garantir ordenação temporal absoluta
    df = df.sort_values('Data').reset_index(drop=True)
    
    # Criar tabela auxiliar de resultados por equipa (Casa e Fora misturados)
    # Empilhar jogos casa e fora para ter a cronologia completa de cada equipa
    home_games = df[['Data', 'Equipa_Casa', 'Golos_Casa_Final', 'Golos_Visitante_Final', 'Resultado_Final']].rename(
        columns={'Equipa_Casa': 'Team', 'Golos_Casa_Final': 'GF', 'Golos_Visitante_Final': 'GA', 'Resultado_Final': 'Res'}
    )
    home_games['Pts'] = home_games['Res'].map({'H': 3, 'D': 1, 'A': 0})
    home_games['Venue'] = 'Home'
    home_games['MatchID'] = df.index  # Manter referência ao jogo original

    away_games = df[['Data', 'Equipa_Visitante', 'Golos_Visitante_Final', 'Golos_Casa_Final', 'Resultado_Final']].rename(
        columns={'Equipa_Visitante': 'Team', 'Golos_Visitante_Final': 'GF', 'Golos_Casa_Final': 'GA', 'Resultado_Final': 'Res'}
    )
    away_games['Pts'] = away_games['Res'].map({'A': 3, 'D': 1, 'H': 0})
    away_games['Venue'] = 'Away'
    away_games['MatchID'] = df.index

    # Juntar tudo e ordenar
    # Isto cria uma longa lista de jogos: Equipa A vs B (Jogo 1) e Equipa B vs A (Jogo 1)
    team_stats = pd.concat([home_games, away_games]).sort_values(['Team', 'Data'])
    
    # Calcular Rolling Stats 
    # SHIFT(1) É CRÍTICO: Para o jogo de hoje, quero a forma dos 5 jogos *anteriores*
    # Se não fizermos shift, usamos o resultado do próprio jogo para prever o jogo => Data Leakage!
    
    print(f"Calculando médias móveis (Janela={window})...")
    
    # Form_Pts5: Soma de Pontos nos últimos 5 jogos
    team_stats['Form_Pts'] = team_stats.groupby('Team')['Pts'].transform(
        lambda x: x.shift(1).rolling(window=window, min_periods=1).sum().fillna(0)
    )
    
    # Form_GM5: Média Golos Marcados ultimos 5
    team_stats['Form_GM'] = team_stats.groupby('Team')['GF'].transform(
        lambda x: x.shift(1).rolling(window=window, min_periods=1).mean().fillna(0)
    )
    
    # Form_GS5: Média Golos Sofridos ultimos 5
    team_stats['Form_GS'] = team_stats.groupby('Team')['GA'].transform(
        lambda x: x.shift(1).rolling(window=window, min_periods=1).mean().fillna(0)
    )

    # Form_Empates5: Numero de Empates nos ultimos 5 jogos
    # Criar flag de empate: 1 se D, 0 caso contrário
    team_stats['IsDraw'] = (team_stats['Res'] == 'D').astype(int)
    team_stats['Form_Empates'] = team_stats.groupby('Team')['IsDraw'].transform(
        lambda x: x.shift(1).rolling(window=window, min_periods=1).sum().fillna(0)
    )

    # Voltar a colocar no dataframe original usando o MatchID
    # Separar Casa e Fora
    print("A fazer merge de volta ao dataset original...")
    
    stats_home = team_stats[team_stats['Venue'] == 'Home'].set_index('MatchID')[['Form_Pts', 'Form_GM', 'Form_GS', 'Form_Empates']]
    stats_home.columns = [f'Casa_{c}{window}' for c in stats_home.columns] # Ex: Casa_Form_Pts5
    
    stats_away = team_stats[team_stats['Venue'] == 'Away'].set_index('MatchID')[['Form_Pts', 'Form_GM', 'Form_GS', 'Form_Empates']]
    stats_away.columns = [f'Visitante_{c}{window}' for c in stats_away.columns] # Ex: Visitante_Form_Pts5
    
    # Juntar ao DF original
    df_enriched = df.join(stats_home).join(stats_away)
    
    return df_enriched

# Execução
try:
    print(f"A ler ficheiro: {INPUT_FILE}")
    df = pd.read_csv(INPUT_FILE)
    
    df_new = calculate_rolling_features(df, window=WINDOW)
    
    # Guardar
    print(f"A guardar ficheiro atualizado: {OUTPUT_FILE}")
    df_new.to_csv(OUTPUT_FILE, index=False)
    print("Sucesso! Novas features criadas:")
    print(df_new.iloc[0:5][[f'Casa_Form_Pts{WINDOW}', f'Visitante_Form_Pts{WINDOW}']])
    
except Exception as e:
    print(f"Erro fatal: {e}")
