import pandas as pd
import numpy as np
from scipy.stats import poisson

# Load historical features dataset
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

# Test BTTS and Clean Sheets
# BTTS flag is 1 if both score, 0 otherwise
# Clean Sheet flag is 1 if opponent scores 0, 0 otherwise
# Reset at the start of each season, carry 0.5 prior for BTTS and 0.3 prior for Clean Sheet on Jornada 1
# Wait! Let's verify if they reset at the start of each season or carry over!
# We will test BOTH resetting and carry-over. Let's write the code to test resetting.

df['Calc_Casa_BTTS_Rate_5J'] = 0.5
df['Calc_Visitante_BTTS_Rate_5J'] = 0.5
df['Calc_Casa_CleanSheet_Rate_5J'] = 0.3
df['Calc_Visitante_CleanSheet_Rate_5J'] = 0.3

# Rolling Shots, Corners, Shots on Target (prior is NaN before 17/18 and on Jornada 1)
df['Calc_Casa_Rolling5_Remates'] = np.nan
df['Calc_Visitante_Rolling5_Remates'] = np.nan
df['Calc_Casa_Rolling5_RematesAlvo'] = np.nan
df['Calc_Visitante_Rolling5_RematesAlvo'] = np.nan
df['Calc_Casa_Rolling5_Cantos'] = np.nan
df['Calc_Visitante_Rolling5_Cantos'] = np.nan

for season in df['Epoca'].unique():
    df_s = df[df['Epoca'] == season]
    team_btts = {} # team -> list
    team_cs = {} # team -> list
    team_remates = {} # team -> list
    team_remates_alvo = {} # team -> list
    team_cantos = {} # team -> list
    
    for idx, row in df_s.iterrows():
        home = row['Equipa_Casa']
        away = row['Equipa_Visitante']
        
        jornada = row['Jornada']
        
        # 1. BTTS Rate
        h_btts_list = team_btts.get(home, [])
        a_btts_list = team_btts.get(away, [])
        
        w_h = min(len(h_btts_list), 5)
        w_a = min(len(a_btts_list), 5)
        
        df.loc[idx, 'Calc_Casa_BTTS_Rate_5J'] = sum(h_btts_list[-w_h:]) / w_h if w_h > 0 else 0.5
        df.loc[idx, 'Calc_Visitante_BTTS_Rate_5J'] = sum(a_btts_list[-w_a:]) / w_a if w_a > 0 else 0.5
        
        # 2. Clean Sheet Rate
        h_cs_list = team_cs.get(home, [])
        a_cs_list = team_cs.get(away, [])
        
        w_cs_h = min(len(h_cs_list), 5)
        w_cs_a = min(len(a_cs_list), 5)
        
        df.loc[idx, 'Calc_Casa_CleanSheet_Rate_5J'] = sum(h_cs_list[-w_cs_h:]) / w_cs_h if w_cs_h > 0 else 0.3
        df.loc[idx, 'Calc_Visitante_CleanSheet_Rate_5J'] = sum(a_cs_list[-w_cs_a:]) / w_cs_a if w_cs_a > 0 else 0.3
        
        # 3. Rolling Shots, Remates Alvo, Cantos (only for 2017-2018 onwards)
        # prior is NaN before season 17/18 and on Jornada 1
        year = int(season.split('-')[0])
        if year >= 2017:
            h_rem = team_remates.get(home, [])
            a_rem = team_remates.get(away, [])
            h_rem_alvo = team_remates_alvo.get(home, [])
            a_rem_alvo = team_remates_alvo.get(away, [])
            h_can = team_cantos.get(home, [])
            a_can = team_cantos.get(away, [])
            
            w_rem_h = min(len(h_rem), 5)
            w_rem_a = min(len(a_rem), 5)
            
            if w_rem_h > 0:
                df.loc[idx, 'Calc_Casa_Rolling5_Remates'] = sum(h_rem[-w_rem_h:]) / w_rem_h
                df.loc[idx, 'Calc_Casa_Rolling5_RematesAlvo'] = sum(h_rem_alvo[-w_rem_h:]) / w_rem_h
                df.loc[idx, 'Calc_Casa_Rolling5_Cantos'] = sum(h_can[-w_rem_h:]) / w_rem_h
                
            if w_rem_a > 0:
                df.loc[idx, 'Calc_Visitante_Rolling5_Remates'] = sum(a_rem[-w_rem_a:]) / w_rem_a
                df.loc[idx, 'Calc_Visitante_Rolling5_RematesAlvo'] = sum(a_rem_alvo[-w_rem_a:]) / w_rem_a
                df.loc[idx, 'Calc_Visitante_Rolling5_Cantos'] = sum(a_can[-w_rem_a:]) / w_rem_a
                
        # Update histories after the match
        hg = row['Golos_Casa_Final']
        ag = row['Golos_Visitante_Final']
        
        btts_val = 1.0 if hg > 0 and ag > 0 else 0.0
        h_cs_val = 1.0 if ag == 0 else 0.0
        a_cs_val = 1.0 if hg == 0 else 0.0
        
        if home not in team_btts:
            team_btts[home] = []
            team_cs[home] = []
            team_remates[home] = []
            team_remates_alvo[home] = []
            team_cantos[home] = []
        if away not in team_btts:
            team_btts[away] = []
            team_cs[away] = []
            team_remates[away] = []
            team_remates_alvo[away] = []
            team_cantos[away] = []
            
        team_btts[home].append(btts_val)
        team_cs[home].append(h_cs_val)
        team_btts[away].append(btts_val)
        team_cs[away].append(a_cs_val)
        
        # Shots/Corners (if year >= 2017)
        if year >= 2017:
            team_remates[home].append(row['Remates_Casa'])
            team_remates_alvo[home].append(row['Remates_Alvo_Casa'])
            team_cantos[home].append(row['Cantos_Casa'])
            
            team_remates[away].append(row['Remates_Visitante'])
            team_remates_alvo[away].append(row['Remates_Alvo_Visitante'])
            team_cantos[away].append(row['Cantos_Visitante'])

# Calculate Poisson
def compute_poisson_draw(l1, l2):
    if np.isnan(l1) or np.isnan(l2):
        return np.nan
    return sum(poisson.pmf(k, l1) * poisson.pmf(k, l2) for k in range(50))

df['Calc_Prob_Empate_Poisson'] = df.apply(lambda r: compute_poisson_draw(r['Casa_ExpectedGolos'], r['Visitante_ExpectedGolos']), axis=1)

# Check errors
btts_clean = df.dropna(subset=['Casa_BTTS_Rate_5J', 'Visitante_BTTS_Rate_5J'])
err_casa_btts = (btts_clean['Calc_Casa_BTTS_Rate_5J'] - btts_clean['Casa_BTTS_Rate_5J']).abs()
print("BTTS Rate Verification (with season resets):")
print(f"  Casa_BTTS Max absolute error: {err_casa_btts.max():.6f}")
print(f"  Casa_BTTS Mismatches (>1e-5): {(err_casa_btts > 1e-5).sum()}")

cs_clean = df.dropna(subset=['Casa_CleanSheet_Rate_5J', 'Visitante_CleanSheet_Rate_5J'])
err_casa_cs = (cs_clean['Calc_Casa_CleanSheet_Rate_5J'] - cs_clean['Casa_CleanSheet_Rate_5J']).abs()
print("\nClean Sheet Rate Verification (with season resets):")
print(f"  Casa_CleanSheet Max absolute error: {err_casa_cs.max():.6f}")
print(f"  Casa_CleanSheet Mismatches (>1e-5): {(err_casa_cs > 1e-5).sum()}")

rem_clean = df.dropna(subset=['Casa_Rolling5_Remates', 'Visitante_Rolling5_Remates'])
err_casa_rem = (rem_clean['Calc_Casa_Rolling5_Remates'] - rem_clean['Casa_Rolling5_Remates']).abs()
print("\nRolling Shots Verification (with season resets):")
print(f"  Casa_Remates Max absolute error: {err_casa_rem.max():.6f}")
print(f"  Casa_Remates Mismatches (>1e-5): {(err_casa_rem > 1e-5).sum()}")

poisson_clean = df.dropna(subset=['Prob_Empate_Poisson'])
err_poisson = (poisson_clean['Calc_Prob_Empate_Poisson'] - poisson_clean['Prob_Empate_Poisson']).abs()
print("\nPoisson Draw Probability Verification:")
print(f"  Poisson Max absolute error: {err_poisson.max():.6f}")
print(f"  Poisson Mismatches (>1e-3): {(err_poisson > 1e-3).sum()}")
