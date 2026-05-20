import pandas as pd
import numpy as np
from scipy.stats import poisson
import math

# Load the historical features dataset
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

# Test Elo ratings
# Starting at 1500.0, carrying over across seasons
K = 20
H = 0
elo_ratings = {} # team -> current elo

df['Calc_Casa_Elo'] = 1500.0
df['Calc_Visitante_Elo'] = 1500.0

for idx, row in df.iterrows():
    home = row['Equipa_Casa']
    away = row['Equipa_Visitante']
    
    # Get pre-game elos
    h_elo = elo_ratings.get(home, 1500.0)
    a_elo = elo_ratings.get(away, 1500.0)
    
    df.loc[idx, 'Calc_Casa_Elo'] = h_elo
    df.loc[idx, 'Calc_Visitante_Elo'] = a_elo
    
    # Update elos after the game
    res = row['Resultado_Final']
    if res == 'H':
        S_h, S_a = 1.0, 0.0
    elif res == 'D':
        S_h, S_a = 0.5, 0.5
    else:
        S_h, S_a = 0.0, 1.0
        
    E_h = 1.0 / (1.0 + 10.0 ** ((a_elo - h_elo - H) / 400.0))
    E_a = 1.0 - E_h
    
    elo_ratings[home] = h_elo + K * (S_h - E_h)
    elo_ratings[away] = a_elo + K * (S_a - E_a)

df['Calc_Diff_Elo'] = df['Calc_Casa_Elo'] - df['Calc_Visitante_Elo']

# Check ELO errors
df_elo_clean = df.dropna(subset=['Casa_Elo_PreJogo', 'Visitante_Elo_PreJogo', 'Diff_Elo'])
err_casa_elo = (df_elo_clean['Calc_Casa_Elo'] - df_elo_clean['Casa_Elo_PreJogo']).abs().max()
err_visi_elo = (df_elo_clean['Calc_Visitante_Elo'] - df_elo_clean['Visitante_Elo_PreJogo']).abs().max()
err_diff_elo = (df_elo_clean['Calc_Diff_Elo'] - df_elo_clean['Diff_Elo']).abs().max()

print("ELO Ratings Verification:")
print(f"  Casa_Elo Max absolute error: {err_casa_elo:.6f}")
print(f"  Visitante_Elo Max absolute error: {err_visi_elo:.6f}")
print(f"  Diff_Elo Max absolute error: {err_diff_elo:.6f}")

# Test Expected Goals
df['Calc_Casa_ExpectedGolos'] = np.nan
df['Calc_Visitante_ExpectedGolos'] = np.nan

# Keep track of goals within each season for rolling averages
for season in df['Epoca'].unique():
    df_s = df[df['Epoca'] == season]
    team_goals_scored = {} # team -> list
    team_goals_conceded = {} # team -> list
    
    for idx, row in df_s.iterrows():
        home = row['Equipa_Casa']
        away = row['Equipa_Visitante']
        
        jornada = row['Jornada']
        
        # Calculate priors
        if jornada == 1:
            # Home expected goals = (Home_hist_Att + Away_hist_Def) / 2.0
            # Away expected goals = (Away_hist_Att + Home_hist_Def) / 2.0
            # Fallbacks: Casa = 1.3, Visitante = 1.1 if NaNs
            h_att = row['Home_hist_Att'] if not np.isnan(row['Home_hist_Att']) else 1.3
            a_def = row['Away_hist_Def'] if not np.isnan(row['Away_hist_Def']) else 1.1
            a_att = row['Away_hist_Att'] if not np.isnan(row['Away_hist_Att']) else 1.1
            h_def = row['Home_hist_Def'] if not np.isnan(row['Home_hist_Def']) else 1.3
            
            calc_casa_xg = (h_att + a_def) / 2.0
            calc_visi_xg = (a_att + h_def) / 2.0
        else:
            # Expanding / 10-match rolling window within season
            h_scored = team_goals_scored.get(home, [])
            h_conceded = team_goals_conceded.get(home, [])
            a_scored = team_goals_scored.get(away, [])
            a_conceded = team_goals_conceded.get(away, [])
            
            # w = min(len, 10)
            w_h = min(len(h_scored), 10)
            w_a = min(len(a_scored), 10)
            
            h_avg_scored = sum(h_scored[-w_h:]) / w_h if w_h > 0 else 1.3
            h_avg_conceded = sum(h_conceded[-w_h:]) / w_h if w_h > 0 else 1.3
            a_avg_scored = sum(a_scored[-w_a:]) / w_a if w_a > 0 else 1.1
            a_avg_conceded = sum(a_conceded[-w_a:]) / w_a if w_a > 0 else 1.1
            
            calc_casa_xg = (h_avg_scored + a_avg_conceded) / 2.0
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

# Check Expected Goals errors
df_xg_clean = df.dropna(subset=['Casa_ExpectedGolos', 'Visitante_ExpectedGolos'])
err_casa_xg = (df_xg_clean['Calc_Casa_ExpectedGolos'] - df_xg_clean['Casa_ExpectedGolos']).abs()
err_visi_xg = (df_xg_clean['Calc_Visitante_ExpectedGolos'] - df_xg_clean['Visitante_ExpectedGolos']).abs()

print("\nExpected Goals Verification:")
print(f"  Casa_ExpectedGolos Max absolute error: {err_casa_xg.max():.6f}")
print(f"  Casa_ExpectedGolos Mean absolute error: {err_casa_xg.mean():.6f}")
print(f"  Casa_ExpectedGolos Mismatches (>1e-5): {(err_casa_xg > 1e-5).sum()}")
print(f"  Visitante_ExpectedGolos Max absolute error: {err_visi_xg.max():.6f}")
print(f"  Visitante_ExpectedGolos Mean absolute error: {err_visi_xg.mean():.6f}")
print(f"  Visitante_ExpectedGolos Mismatches (>1e-5): {(err_visi_xg > 1e-5).sum()}")

if (err_casa_xg > 1e-5).sum() > 0:
    print("\nSample Expected Goals mismatches:")
    mismatch_df = df_xg_clean[err_casa_xg > 1e-5]
    for idx, row in mismatch_df.head(5).iterrows():
        print(f"Row {idx}: {row['Equipa_Casa']} vs {row['Equipa_Visitante']}, Jornada {row['Jornada']}, Epoca {row['Epoca']}")
        print(f"  Actual Casa xG: {row['Casa_ExpectedGolos']:.4f}, Calc: {row['Calc_Casa_ExpectedGolos']:.4f}")
