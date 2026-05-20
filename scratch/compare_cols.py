import pandas as pd

v2_path = r"d:\Diogo\Ambiente de Trabalho\PROJETO\Datasets\dataset_final_merged_v2.csv"
adv_path = r"d:\Diogo\Ambiente de Trabalho\PROJETO\Datasets\dataset_features_avancadas.csv"

try:
    df_v2 = pd.read_csv(v2_path, encoding='latin1', low_memory=False)
    print("V2 shape:", df_v2.shape)
except Exception as e:
    print("Error reading V2:", e)
    df_v2 = None

try:
    df_adv = pd.read_csv(adv_path, encoding='latin1', low_memory=False)
    print("Adv shape:", df_adv.shape)
except Exception as e:
    print("Error reading Adv:", e)
    df_adv = None

if df_v2 is not None and df_adv is not None:
    v2_cols = set(df_v2.columns)
    adv_cols = set(df_adv.columns)
    
    only_v2 = v2_cols - adv_cols
    only_adv = adv_cols - v2_cols
    common = v2_cols & adv_cols
    
    print("\nOnly in V2:", len(only_v2))
    print(sorted(list(only_v2)))
    
    print("\nOnly in Adv:", len(only_adv))
    print(sorted(list(only_adv)))
    
    print("\nCommon columns:", len(common))
