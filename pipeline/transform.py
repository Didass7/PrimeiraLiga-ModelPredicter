import os
import pandas as pd
import numpy as np

# Mapeamento oficial para uniformizar os nomes das equipas entre FBRef e Football-Data
TEAM_NAME_MAPPING = {
    # Football-Data name -> Clean Historical Name (matches FBRef)
    "AVS": "AVS Futebol",
    "Academica": "Académica",
    "Beira Mar": "Beira-Mar",
    "Famalicao": "Famalicão",
    "Maritimo": "Marítimo",
    "Pacos Ferreira": "Paços de Ferreira",
    "Sp Braga": "Braga",
    "Sp Lisbon": "Sporting CP",
    "Setubal": "Vitória Setúbal",
    "Uniao Madeira": "União",
    "Guimaraes": "Vitória",
    "Gil Vicente": "Gil Vicente",
    "Nacional": "Nacional",
    "Estrela": "Estrela",
    "Leiria": "União de Leiria",
    "Leixoes": "Leixões",
    "Feirense": "Feirense",
    "Belenenses": "Belenenses",
    "Martimo": "Marítimo",
    "Vitria Setǧbal": "Vitória Setúbal",
    "Paos de Ferreira": "Paços de Ferreira",
    "Vitria Guimares": "Vitória",
    "Olhannse": "Olhanense",
    "Naval": "Naval 1º de Maio"
}

# Caminhos
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FBREF_DATABASE_PATH = os.path.join(ROOT_DIR, "Datasets", "FBRef", "dataset_completo_final.csv")

def normalize_team_names(df, home_col, away_col):
    """
    Normaliza os nomes das equipas em ambas as colunas (casa/fora).
    """
    if df is None:
        return None
    df = df.copy()
    if home_col in df.columns:
        df[home_col] = df[home_col].str.strip().replace(TEAM_NAME_MAPPING)
    if away_col in df.columns:
        df[away_col] = df[away_col].str.strip().replace(TEAM_NAME_MAPPING)
    return df

def merge_sources(df_fd, df_fbref=None):
    """
    Junta as duas fontes de dados: Football-Data e FBRef.
    1. Renomeia as colunas de Football-Data para Português.
    2. Carrega a base histórica do FBRef localmente.
    3. Calcula a média das 3 piores equipas por época do FBRef (relegation zone).
    4. Junta as estatísticas históricas da época anterior para a equipa da Casa e Visitante.
    5. Imputa os valores estatísticos de recém-promovidos usando as médias de despromoção.
    """
    print("[Transform] A iniciar o merge das duas fontes de dados...")
    
    if df_fd is None:
        print("[Transform] Erro: Dados do Football-Data são obrigatórios.")
        return None
        
    df_fd = df_fd.copy()
    
    # 1. Renomeação de colunas do Football-Data para Português
    col_map_pt = {
        'Date': 'Data', 'Time': 'Hora', 'HomeTeam': 'Equipa_Casa', 'AwayTeam': 'Equipa_Visitante',
        'FTHG': 'Golos_Casa_Final', 'FTAG': 'Golos_Visitante_Final', 'FTR': 'Resultado_Final',
        'HTHG': 'Golos_Casa_Intervalo', 'HTAG': 'Golos_Visitante_Intervalo', 'HTR': 'Resultado_Intervalo',
        'HS': 'Remates_Casa', 'AS': 'Remates_Visitante', 'HST': 'Remates_Alvo_Casa', 'AST': 'Remates_Alvo_Visitante',
        'HF': 'Faltas_Casa', 'AF': 'Faltas_Visitante', 'HC': 'Cantos_Casa', 'AC': 'Cantos_Visitante',
        'HY': 'Amarelos_Casa', 'AY': 'Amarelos_Visitante', 'HR': 'Vermelhos_Casa', 'AR': 'Vermelhos_Visitante',
        'B365H': 'Odd_Casa_Bet365', 'B365D': 'Odd_Empate_Bet365', 'B365A': 'Odd_Visitante_Bet365',
        'AvgH': 'Odd_Casa_Media', 'AvgD': 'Odd_Empate_Media', 'AvgA': 'Odd_Visitante_Media'
    }
    df_fd = df_fd.rename(columns={k: v for k, v in col_map_pt.items() if k in df_fd.columns})
    df_fd = normalize_team_names(df_fd, 'Equipa_Casa', 'Equipa_Visitante')
    
    # 2. Carregar dados históricos do FBRef
    if not os.path.exists(FBREF_DATABASE_PATH):
        print(f"[Transform] Erro: Banco de dados FBRef não encontrado em {FBREF_DATABASE_PATH}.")
        print("[Transform] Continuando apenas com os dados do Football-Data (esqueleto)...")
        return df_fd

    try:
        df_fbref_db = pd.read_csv(FBREF_DATABASE_PATH, encoding='latin1')
    except Exception as e:
        print(f"[Transform] Erro ao ler banco de dados FBRef: {e}. Continuando sem FBRef...")
        return df_fd
        
    # Assegurar formato de data e ordenar temporariamente para calcular Epoca
    df_fd['Data'] = pd.to_datetime(df_fd['Data'], dayfirst=True, errors='coerce')
    df_fd = df_fd.dropna(subset=['Data']).sort_values('Data').reset_index(drop=True)
    
    # Calcular Época Atual e Anterior (Previous_Season)
    def get_season(date):
        return f"{date.year}-{date.year+1}" if date.month >= 7 else f"{date.year-1}-{date.year}"
    df_fd['Epoca'] = df_fd['Data'].apply(get_season)
    df_fd['Previous_Season'] = df_fd['Epoca'].apply(lambda x: f"{int(x.split('-')[0])-1}-{int(x.split('-')[0])}")

    # 3. IMPUTAÇÃO: Calcular médias das 3 piores equipas (zona de despromoção) por época
    print("[Transform] A calcular estatísticas de imputação de despromoção (Relegation Zone)...")
    relegation_stats = []
    for season in df_fbref_db['Epoca'].unique():
        season_data = df_fbref_db[df_fbref_db['Epoca'] == season].sort_values('Pontos')
        if not season_data.empty:
            bottom_3 = season_data.head(3).mean(numeric_only=True)
            bottom_3['Epoca'] = season
            relegation_stats.append(bottom_3)
    df_relegation = pd.DataFrame(relegation_stats)

    # Preparar df_hist com prefixo hist_
    df_hist = df_fbref_db.copy()
    stats_cols = [c for c in df_hist.columns if c not in ['Equipa', 'Epoca']]
    rename_cols = {c: f"hist_{c}" for c in stats_cols}
    df_hist = df_hist.rename(columns=rename_cols)

    # Preparar df_relegation com prefixo hist_
    df_relegation_renamed = df_relegation.rename(columns={c: f"hist_{c}" for c in stats_cols})

    # 4. Merge de Estatísticas Históricas da Equipa da Casa
    print("[Transform] A cruzar dados históricos da Equipa da Casa...")
    df_merged = pd.merge(df_fd, df_hist, left_on=['Equipa_Casa', 'Previous_Season'], right_on=['Equipa', 'Epoca'], how='left')
    df_merged = df_merged.drop(columns=['Equipa', 'Epoca_y'], errors='ignore')
    if 'Epoca_x' in df_merged.columns:
        df_merged = df_merged.rename(columns={'Epoca_x': 'Epoca'})
        
    rename_home = {f"hist_{c}": f"Home_hist_{c}" for c in stats_cols}
    df_merged = df_merged.rename(columns=rename_home)

    # Imputação da Casa para equipas recém-promovidas
    df_defaults_home = pd.merge(df_merged[['Previous_Season']], df_relegation_renamed, left_on='Previous_Season', right_on='Epoca', how='left')
    rename_home_defaults = {f"hist_{c}": f"Home_hist_{c}" for c in stats_cols}
    df_defaults_home = df_defaults_home.rename(columns=rename_home_defaults)
    
    for c in stats_cols:
        col_name = f"Home_hist_{c}"
        if col_name in df_merged.columns:
            df_merged[col_name] = df_merged[col_name].fillna(df_defaults_home[col_name])

    # 5. Merge de Estatísticas Históricas da Equipa Visitante
    print("[Transform] A cruzar dados históricos da Equipa Visitante...")
    df_merged = pd.merge(df_merged, df_hist, left_on=['Equipa_Visitante', 'Previous_Season'], right_on=['Equipa', 'Epoca'], how='left')
    df_merged = df_merged.drop(columns=['Equipa', 'Epoca_y'], errors='ignore')
    if 'Epoca_x' in df_merged.columns:
        df_merged = df_merged.rename(columns={'Epoca_x': 'Epoca'})
        
    rename_away = {f"hist_{c}": f"Away_hist_{c}" for c in stats_cols}
    df_merged = df_merged.rename(columns=rename_away)

    # Imputação de Visitante para equipas recém-promovidas
    df_defaults_away = pd.merge(df_merged[['Previous_Season']], df_relegation_renamed, left_on='Previous_Season', right_on='Epoca', how='left')
    rename_away_defaults = {f"hist_{c}": f"Away_hist_{c}" for c in stats_cols}
    df_defaults_away = df_defaults_away.rename(columns=rename_away_defaults)
    
    for c in stats_cols:
        col_name = f"Away_hist_{c}"
        if col_name in df_merged.columns:
            df_merged[col_name] = df_merged[col_name].fillna(df_defaults_away[col_name])

    print(f"[Transform] Sucesso! Merge e Imputação de Promovidos concluídos. Shape: {df_merged.shape}")
    return df_merged

def compute_pipeline_features(df):
    """
    Aplica o cálculo dinâmico da Jornada e garante a ordenação temporal absoluta.
    """
    print("[Transform] A aplicar ordenação e cálculo dinâmico de Jornada...")
    if df is None:
        return None
        
    df = df.copy()
    
    # Garantir datetime
    df['Data'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Data']).sort_values('Data').reset_index(drop=True)
    
    # Calcular Jornada
    def compute_jornadas(season_df):
        season_df = season_df.copy()
        team_games = {}
        jornadas = []
        for _, row in season_df.iterrows():
            home = row['Equipa_Casa']
            away = row['Equipa_Visitante']
            hg = team_games.get(home, 0)
            ag = team_games.get(away, 0)
            matchday = max(hg, ag) + 1
            jornadas.append(matchday)
            team_games[home] = hg + 1
            team_games[away] = ag + 1
        season_df['Jornada'] = jornadas
        return season_df
        
    df = df.groupby('Epoca', group_keys=False).apply(compute_jornadas).sort_values('Data').reset_index(drop=True)
    return df

if __name__ == "__main__":
    print("Script de Transformação carregado com sucesso.")
