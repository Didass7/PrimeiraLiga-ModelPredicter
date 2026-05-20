import pandas as pd
import numpy as np

# Load dataset
df = pd.read_csv(r"d:\Diogo\Ambiente de Trabalho\PROJETO\Datasets\dataset_features_avancadas.csv", encoding="latin1", low_memory=False)
df['Data'] = pd.to_datetime(df['Data'])
df = df.sort_values('Data').reset_index(drop=True)

# Find first row where Remates_Casa is not nan
df_shots = df.dropna(subset=['Remates_Casa', 'Casa_Rolling5_Remates']).copy()
if not df_shots.empty:
    first_row = df_shots.iloc[0]
    season = first_row['Season']
    print(f"Shots and rolling features start in season: {season}")
    
    # Let's track a team in that season
    team = first_row['Equipa_Casa']
    team_matches = df[((df['Equipa_Casa'] == team) | (df['Equipa_Visitante'] == team)) & (df['Season'] == season)].copy()
    team_matches = team_matches.sort_values('Data')
    
    print(f"\n{team} matches in {season}:")
    for idx, row in team_matches.head(10).iterrows():
        role = 'Casa' if row['Equipa_Casa'] == team else 'Visitante'
        opp = row['Equipa_Visitante'] if role == 'Casa' else row['Equipa_Casa']
        
        # Actual shots and corners in the game
        sh = row['Remates_Casa'] if role == 'Casa' else row['Remates_Visitante']
        sha = row['Remates_Alvo_Casa'] if role == 'Casa' else row['Remates_Alvo_Visitante']
        corners = row['Cantos_Casa'] if role == 'Casa' else row['Cantos_Visitante']
        
        # Rolling averages
        r_sh = row['Casa_Rolling5_Remates'] if role == 'Casa' else row['Visitante_Rolling5_Remates']
        r_sha = row['Casa_Rolling5_RematesAlvo'] if role == 'Casa' else row['Visitante_Rolling5_RematesAlvo']
        r_corners = row['Casa_Rolling5_Cantos'] if role == 'Casa' else row['Visitante_Rolling5_Cantos']
        
        print(f"vs {opp} ({role}) | Shot={sh}, ShotOnTarg={sha}, Corn={corners} | CSV Rolling: Rem={r_sh}, RemAlvo={r_sha}, Cantos={r_corners}")
else:
    print("No rows found with non-nan shots and rolling features!")
