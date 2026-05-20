import pandas as pd
import numpy as np

# Load the advanced features dataset
df = pd.read_csv(r"d:\Diogo\Ambiente de Trabalho\PROJETO\Datasets\dataset_features_avancadas.csv", encoding="latin1", low_memory=False)
df['Data'] = pd.to_datetime(df['Data'])
df = df.sort_values('Data').reset_index(drop=True)

# Let's group by Season and find a team's games in a season
braga_2010 = df[((df['Equipa_Casa'] == 'Braga') | (df['Equipa_Visitante'] == 'Braga')) & (df['Season'] == '2010-2011')].copy()

print("Braga 2010-2011 games:")
for idx, row in braga_2010.head(10).iterrows():
    role = 'Casa' if row['Equipa_Casa'] == 'Braga' else 'Visitante'
    opp = row['Equipa_Visitante'] if role == 'Casa' else row['Equipa_Casa']
    gf = row['Golos_Casa_Final'] if role == 'Casa' else row['Golos_Visitante_Final']
    ga = row['Golos_Visitante_Final'] if role == 'Casa' else row['Golos_Casa_Final']
    
    f_pts = row['Casa_Form_Pts5'] if role == 'Casa' else row['Visitante_Form_Pts5']
    f_gm = row['Casa_Form_GM5'] if role == 'Casa' else row['Visitante_Form_GM5']
    f_gs = row['Casa_Form_GS5'] if role == 'Casa' else row['Visitante_Form_GS5']
    f_emp = row['Casa_Form_Empates5'] if role == 'Casa' else row['Visitante_Form_Empates5']
    btts = row['Casa_BTTS_Rate_5J'] if role == 'Casa' else row['Visitante_BTTS_Rate_5J']
    cs = row['Casa_CleanSheet_Rate_5J'] if role == 'Casa' else row['Visitante_CleanSheet_Rate_5J']
    rem = row['Casa_Rolling5_Remates'] if role == 'Casa' else row['Visitante_Rolling5_Remates']
    
    print(f"vs {opp} ({role}) | GF={gf}, GA={ga} | CSV rolling: Pts={f_pts}, GM={f_gm}, GS={f_gs}, Emp={f_emp}, BTTS={btts}, CS={cs}, Rem={rem}")
