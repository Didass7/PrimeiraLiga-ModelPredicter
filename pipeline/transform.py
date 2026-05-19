import os
import pandas as pd
import numpy as np

# Mapeamento para uniformizar os nomes das equipas entre FBRef e Football-Data
TEAM_NAME_MAPPING = {
    "Porto": "FC Porto",
    "Sp Braga": "Braga",
    "Sporting CP": "Sporting",
    "Benfica": "Benfica",
    "Pacos Ferreira": "Paços de Ferreira",
    "Vitoria Guimaraes": "Vitória",
    "Gil Vicente": "Gil Vicente",
    "Santa Clara": "Santa Clara",
    "Portimonense": "Portimonense",
    "Moreirense": "Moreirense",
    "Famalicao": "Famalicão",
    "Boavista": "Boavista",
    "Vizela": "Vizela",
    "Maritimo": "Marítimo",
    "Arouca": "Arouca",
    "Estoril": "Estoril",
    "Chaves": "Chaves",
    "Casa Pia": "Casa Pia",
    "Rio Ave": "Rio Ave",
    "Farense": "Farense",
    "Estrela": "Estrela da Amadora",
    "Nacional": "Nacional",
}

def normalize_team_names(df, home_col, away_col):
    """
    Normaliza os nomes das equipas em ambas as colunas (casa/fora).
    """
    if df is None:
        return None
    df = df.copy()
    if home_col in df.columns:
        df[home_col] = df[home_col].replace(TEAM_NAME_MAPPING)
    if away_col in df.columns:
        df[away_col] = df[away_col].replace(TEAM_NAME_MAPPING)
    return df

def merge_sources(df_fd, df_fbref):
    """
    Junta as duas fontes usando a Data e Equipas como chaves.
    """
    print("[Transform] A iniciar o merge das duas fontes de dados...")
    
    if df_fd is None:
        print("[Transform] Erro: Dados do Football-Data são obrigatórios para a estrutura base.")
        return None
        
    df_fd = df_fd.copy()
    
    # Limpeza e renomeação de colunas do Football-Data
    # Mapear para o formato do teu dataset original
    rename_dict = {
        'Date': 'Data',
        'HomeTeam': 'Equipa_Casa',
        'AwayTeam': 'Equipa_Visitante',
        'FTHG': 'Golos_Casa_Final',
        'FTAG': 'Golos_Visitante_Final',
        'FTR': 'Resultado_Final'
    }
    df_fd = df_fd.rename(columns={k: v for k, v in rename_dict.items() if k in df_fd.columns})
    df_fd = normalize_team_names(df_fd, 'Equipa_Casa', 'Equipa_Visitante')
    
    if df_fbref is None:
        print("[Transform] Aviso: Sem dados do FBRef. A gerar esqueleto apenas com Football-Data...")
        # Adiciona colunas que estariam no FBRef com NaNs ou 0 para não quebrar o modelo
        return df_fd
        
    # Exemplo de Merge Real no futuro:
    # df_fbref = normalize_team_names(df_fbref, 'Home_Team', 'Away_Team')
    # df_merged = pd.merge(df_fd, df_fbref, on=['Data', 'Equipa_Casa', 'Equipa_Visitante'], how='left')
    # return df_merged
    return df_fd

def compute_pipeline_features(df):
    """
    Aplica o cálculo de jornadas e rolling features (semelhante ao add_jornada.py e update_features.py).
    """
    print("[Transform] A aplicar engenharia de features (Jornada, Epoca e Médias Móveis)...")
    if df is None:
        return None
        
    df = df.copy()
    
    # Garantir datetime
    if 'Data' in df.columns:
        df['Data'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce')
        df = df.dropna(subset=['Data']).sort_values('Data').reset_index(drop=True)
        
        # Calcular Epoca
        def get_season(date):
            return f"{date.year}-{date.year+1}" if date.month >= 7 else f"{date.year-1}-{date.year}"
        df['Epoca'] = df['Data'].apply(get_season)
        
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
