import pandas as pd
import numpy as np

# Load dataset
df = pd.read_csv(r"d:\Diogo\Ambiente de Trabalho\PROJETO\Datasets\dataset_features_avancadas.csv", encoding="latin1", low_memory=False)
df['Data'] = pd.to_datetime(df['Data'])
df = df.sort_values('Data').reset_index(drop=True)

# Add Jornada
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

df = df.groupby('Season', group_keys=False).apply(compute_jornadas).sort_values('Data').reset_index(drop=True)

# Compute rolling 10 goals for each team within each season
df['Roll10_GM_Casa'] = np.nan
df['Roll10_GS_Casa'] = np.nan
df['Roll10_GM_Visi'] = np.nan
df['Roll10_GS_Visi'] = np.nan

for season in df['Season'].unique():
    df_s = df[df['Season'] == season]
    team_games = {} # team -> list of (gf, ga)
    
    for idx, row in df_s.iterrows():
        home, away = row['Equipa_Casa'], row['Equipa_Visitante']
        hg_final, ag_final = row['Golos_Casa_Final'], row['Golos_Visitante_Final']
        
        h_list = team_games.get(home, [])
        a_list = team_games.get(away, [])
        
        # Compute prior rolling 10
        if len(h_list) > 0:
            recent_h = h_list[-10:]
            df.loc[idx, 'Roll10_GM_Casa'] = sum([x[0] for x in recent_h]) / len(recent_h)
            df.loc[idx, 'Roll10_GS_Casa'] = sum([x[1] for x in recent_h]) / len(recent_h)
        if len(a_list) > 0:
            recent_a = a_list[-10:]
            df.loc[idx, 'Roll10_GM_Visi'] = sum([x[0] for x in recent_a]) / len(recent_a)
            df.loc[idx, 'Roll10_GS_Visi'] = sum([x[1] for x in recent_a]) / len(recent_a)
            
        # Update lists after game
        h_list.append((hg_final, ag_final))
        a_list.append((ag_final, hg_final))
        team_games[home] = h_list
        team_games[away] = a_list

# Drop NaNs
df_clean = df.dropna(subset=['Roll10_GM_Casa', 'Roll10_GS_Visi', 'Roll10_GM_Visi', 'Roll10_GS_Casa', 'Casa_ExpectedGolos', 'Visitante_ExpectedGolos']).copy()

# Calculate predicted expected goals
df_clean['pred_casa'] = (df_clean['Roll10_GM_Casa'] + df_clean['Roll10_GS_Visi']) / 2.0
df_clean['pred_visi'] = (df_clean['Roll10_GM_Visi'] + df_clean['Roll10_GS_Casa']) / 2.0

diff_casa = (df_clean['Casa_ExpectedGolos'] - df_clean['pred_casa']).abs()
diff_visi = (df_clean['Visitante_ExpectedGolos'] - df_clean['pred_visi']).abs()

print(f"Rolling 10 across all {len(df_clean)} matches:")
print(f"  Casa xG max absolute diff: {diff_casa.max()}")
print(f"  Casa xG mean absolute diff: {diff_casa.mean()}")
print(f"  Casa xG errors > 1e-4: {(diff_casa > 1e-4).sum()}")
print(f"  Visi xG max absolute diff: {diff_visi.max()}")
print(f"  Visi xG mean absolute diff: {diff_visi.mean()}")
print(f"  Visi xG errors > 1e-4: {(diff_visi > 1e-4).sum()}")

# Print top 5 mismatches if any
if (diff_casa > 1e-4).sum() > 0:
    print("\nTop 5 rolling 10 mismatches:")
    for idx, row in df_clean[diff_casa > 1e-4].head(5).iterrows():
        print(f"Row {idx}: {row['Equipa_Casa']} vs {row['Equipa_Visitante']}, Season {row['Season']}, Jornada {row['Jornada']}")
        print(f"  Actual Casa_xG: {row['Casa_ExpectedGolos']:.4f}, Pred: {row['pred_casa']:.4f}")
        print(f"  Casa_Form_GM5: {row['Casa_Form_GM5']:.4f}, Visitante_Form_GS5: {row['Visitante_Form_GS5']:.4f}")
