import pandas as pd
import numpy as np

# Load our calculation results
df = pd.read_csv(r"d:\Diogo\Ambiente de Trabalho\PROJETO\Datasets\dataset_features_avancadas.csv", encoding="latin1", low_memory=False)
df['Data'] = pd.to_datetime(df['Data'])
df = df.sort_values('Data').reset_index(drop=True)

# 1. Compute Jornada and Season
def get_season(date):
    return f"{date.year}-{date.year+1}" if date.month >= 7 else f"{date.year-1}-{date.year}"
df['Epoca'] = df['Data'].apply(get_season)

def compute_jornadas(season_df):
    season_df = season_df.copy()
    team_games = {}
    jornadas = []
    for _, row in season_df.iterrows():
        home, away = row['Equipa_Casa'], row['Equipa_Visitante']
        hg, ag = team_games.get(home, 0), team_games.get(away, 0)
        matchday = max(hg, ag) + 1
        jornadas.append(matchday)
        team_games[home] = hg + 1
        team_games[away] = ag + 1
    season_df['Jornada'] = jornadas
    return season_df

df = df.groupby('Epoca', group_keys=False).apply(compute_jornadas).sort_values('Data').reset_index(drop=True)

# 2. Historical stats att/def
df['Home_hist_Att'] = df['Home_hist_GolosMarcados'] / df['Home_hist_JogosDisputados']
df['Away_hist_Def'] = df['Away_hist_GolosSofridos'] / df['Away_hist_JogosDisputados']
df['Away_hist_Att'] = df['Away_hist_GolosMarcados'] / df['Away_hist_JogosDisputados']
df['Home_hist_Def'] = df['Home_hist_GolosSofridos'] / df['Home_hist_JogosDisputados']

# Test Expected Goals (with continuous carry-over across seasons!)
df['Calc_Casa_ExpectedGolos'] = np.nan
df['Calc_Visitante_ExpectedGolos'] = np.nan

team_goals_scored = {} # team -> list
team_goals_conceded = {} # team -> list

for idx, row in df.iterrows():
    home = row['Equipa_Casa']
    away = row['Equipa_Visitante']
    
    h_scored = team_goals_scored.get(home, [])
    h_conceded = team_goals_conceded.get(home, [])
    a_scored = team_goals_scored.get(away, [])
    a_conceded = team_goals_conceded.get(away, [])
    
    # Calculate home xG
    if len(h_scored) == 0 or len(a_conceded) == 0:
        h_att = row['Home_hist_Att'] if not np.isnan(row['Home_hist_Att']) else 1.3
        a_def = row['Away_hist_Def'] if not np.isnan(row['Away_hist_Def']) else 1.1
        calc_casa_xg = (h_att + a_def) / 2.0
    else:
        w_h = min(len(h_scored), 10)
        w_a = min(len(a_conceded), 10)
        h_avg_scored = sum(h_scored[-w_h:]) / w_h
        a_avg_conceded = sum(a_conceded[-w_a:]) / w_a
        calc_casa_xg = (h_avg_scored + a_avg_conceded) / 2.0
        
    # Calculate away xG
    if len(a_scored) == 0 or len(h_conceded) == 0:
        a_att = row['Away_hist_Att'] if not np.isnan(row['Away_hist_Att']) else 1.1
        h_def = row['Home_hist_Def'] if not np.isnan(row['Home_hist_Def']) else 1.3
        calc_visi_xg = (a_att + h_def) / 2.0
    else:
        w_h = min(len(h_conceded), 10)
        w_a = min(len(a_scored), 10)
        h_avg_conceded = sum(h_conceded[-w_h:]) / w_h
        a_avg_scored = sum(a_scored[-w_a:]) / w_a
        calc_visi_xg = (a_avg_scored + h_avg_conceded) / 2.0
        
    df.loc[idx, 'Calc_Casa_ExpectedGolos'] = calc_casa_xg
    df.loc[idx, 'Calc_Visitante_ExpectedGolos'] = calc_visi_xg
    
    # Update team goals history after the match
    hg = row['Golos_Casa_Final']
    ag = row['Golos_Visitante_Final']
    
    if home not in team_goals_scored:
        team_goals_scored[home] = []
        team_goals_conceded[home] = []
    if away not in team_goals_scored:
        team_goals_scored[away] = []
        team_goals_conceded[away] = []
        
    team_goals_scored[home].append(hg)
    team_goals_conceded[home].append(ag)
    team_goals_scored[away].append(ag)
    team_goals_conceded[away].append(hg)

# Find mismatches
df_xg_clean = df.dropna(subset=['Casa_ExpectedGolos', 'Visitante_ExpectedGolos']).copy()
df_xg_clean['err_casa'] = (df_xg_clean['Calc_Casa_ExpectedGolos'] - df_xg_clean['Casa_ExpectedGolos']).abs()
df_xg_clean['err_visi'] = (df_xg_clean['Calc_Visitante_ExpectedGolos'] - df_xg_clean['Visitante_ExpectedGolos']).abs()

mismatches = df_xg_clean[(df_xg_clean['err_casa'] > 1e-5) | (df_xg_clean['err_visi'] > 1e-5)]

print(f"Total mismatches: {len(mismatches)}")
print("\nMismatches detailed:")
for idx, row in mismatches.iterrows():
    print(f"Row {idx}: {row['Equipa_Casa']} vs {row['Equipa_Visitante']}, Epoca {row['Epoca']}, Jornada {row['Jornada']}")
    print(f"  Casa xG - Actual: {row['Casa_ExpectedGolos']:.4f}, Calc: {row['Calc_Casa_ExpectedGolos']:.4f}, Err: {row['err_casa']:.4f}")
    print(f"  Visi xG - Actual: {row['Visitante_ExpectedGolos']:.4f}, Calc: {row['Calc_Visitante_ExpectedGolos']:.4f}, Err: {row['err_visi']:.4f}")
    print(f"  Home Hist Att: {row['Home_hist_Att']:.4f}, Away Hist Def: {row['Away_hist_Def']:.4f}")
    print(f"  Away Hist Att: {row['Away_hist_Att']:.4f}, Home Hist Def: {row['Home_hist_Def']:.4f}")
