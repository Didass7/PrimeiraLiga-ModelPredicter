import pandas as pd
import numpy as np

file_path = 'd:/Diogo/Ambiente de Trabalho/PROJETO/Datasets/dataset_final_merged_v2.csv'
print(f"Lendo {file_path}...")
df = pd.read_csv(file_path)

# Garantir que a Data é do tipo datetime
df['Data'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce')
df = df.dropna(subset=['Data']).sort_values('Data').reset_index(drop=True)

# Inferir a Época: a lógica padrão europeia é que jogos a partir de Julho (mês 7) pertencem à época do ano atual - ano seguinte.
def get_season(date):
    if date.month >= 7:
        return f"{date.year}-{date.year+1}"
    else:
        return f"{date.year-1}-{date.year}"

if 'Epoca' not in df.columns:
    df['Epoca'] = df['Data'].apply(get_season)

# Calcular a 'Jornada' do jogo dinamicamente
def compute_jornadas(season_df):
    season_df = season_df.copy()
    team_games = {}
    jornadas = []
    
    for idx, row in season_df.iterrows():
        home = row['Equipa_Casa']
        away = row['Equipa_Visitante']
        
        # O número de jogos que já realizaram nesta época (antes deste jogo)
        home_games = team_games.get(home, 0)
        away_games = team_games.get(away, 0)
        
        # A jornada será o máximo de jogos realizados entre os dois + 1
        matchday = max(home_games, away_games) + 1
        jornadas.append(matchday)
        
        # Atualiza a contagem de jogos efetuados
        team_games[home] = home_games + 1
        team_games[away] = away_games + 1
        
    season_df['Jornada'] = jornadas
    return season_df

print("Calculando Jornadas e agrupando por Época...")
df = df.groupby('Epoca', group_keys=False).apply(compute_jornadas)

# Ordenar finalmente de forma temporal contínua
df = df.sort_values(by=['Data']).reset_index(drop=True)

df.to_csv(file_path, index=False)
print(f"Colunas 'Jornada' e 'Epoca' geradas com sucesso. Guardado em: {file_path}")
