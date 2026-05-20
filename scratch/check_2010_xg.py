import pandas as pd
import numpy as np

# Load dataset
df = pd.read_csv(r"d:\Diogo\Ambiente de Trabalho\PROJETO\Datasets\dataset_features_avancadas.csv", encoding="latin1", low_memory=False)
df['Data'] = pd.to_datetime(df['Data'])
df = df.sort_values('Data').reset_index(drop=True)

# Filter 2010-2011
df_2010 = df[df['Season'] == '2010-2011'].copy()

# Print unique values in Jornada 1
df_2010_j1 = df_2010[df_2010['Casa_Form_Pts5'] == 0.0] # approximate J1
print("Jornada 1 Expected Golos unique values in 2010-2011:")
print("  Casa_ExpectedGolos:", df_2010_j1['Casa_ExpectedGolos'].unique())
print("  Visitante_ExpectedGolos:", df_2010_j1['Visitante_ExpectedGolos'].unique())

# Print first 5 rows of 2010-2011
print("\nFirst 5 matches of 2010-2011:")
print(df_2010[['Equipa_Casa', 'Equipa_Visitante', 'Casa_ExpectedGolos', 'Visitante_ExpectedGolos', 'Casa_Form_GM5', 'Visitante_Form_GS5', 'Visitante_Form_GM5', 'Casa_Form_GS5']].head(5))

# Let's check subsequent jornadas in 2010-2011: does the formula (GM5 + GS5)/2 hold?
df_2010_gt1 = df_2010[df_2010['Casa_Form_Pts5'] > 0.0] # approximate gt1
diff_casa = (df_2010_gt1['Casa_ExpectedGolos'] - (df_2010_gt1['Casa_Form_GM5'] + df_2010_gt1['Visitante_Form_GS5']) / 2.0).abs()
diff_visi = (df_2010_gt1['Visitante_ExpectedGolos'] - (df_2010_gt1['Visitante_Form_GM5'] + df_2010_gt1['Casa_Form_GS5']) / 2.0).abs()
print(f"\nSubsequent Jornadas in 2010-2011:")
print(f"  Casa xG max abs diff with formula (GM5 + GS5)/2: {diff_casa.max()}")
print(f"  Visi xG max abs diff with formula (GM5 + GS5)/2: {diff_visi.max()}")
