import os
import pandas as pd
import numpy as np
from scipy.stats import poisson

# Caminhos do projeto
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HISTORICAL_ADVANCED_PATH = os.path.join(ROOT_DIR, "Datasets", "dataset_features_avancadas.csv")
TARGET_MERGED_PATH = os.path.join(ROOT_DIR, "Datasets", "dataset_final_merged_v2.csv")

def update_advanced_datasets():
    """
    Orquestra o cálculo das 16 advanced features de forma altamente otimizada e atualiza:
    1. dataset_final_merged_v2.csv (completo, com todas as colunas)
    2. dataset_features_avancadas.csv (com exatamente as 326 colunas originais e ordem)
    """
    print("=" * 60)
    print("INICIANDO CÁLCULO E ATUALIZAÇÃO DAS FEATURES AVANÇADAS (OTIMIZADO)")
    print("=" * 60)
    
    # 1. Carregar os datasets
    if not os.path.exists(TARGET_MERGED_PATH):
        print(f"Erro: Ficheiro base {TARGET_MERGED_PATH} não encontrado.")
        return False
        
    print(f"Lendo base mesclada: {TARGET_MERGED_PATH}")
    df_merged = pd.read_csv(TARGET_MERGED_PATH, encoding="latin1", low_memory=False)
    
    # Normalizar datas
    df_merged['Data'] = pd.to_datetime(df_merged['Data'], errors='coerce')
    df_merged = df_merged.dropna(subset=['Data']).sort_values('Data').reset_index(drop=True)
    
    # Padronizar Epoca, Season e Previous_Season
    def get_season(date):
        return f"{date.year}-{date.year+1}" if date.month >= 7 else f"{date.year-1}-{date.year}"
    
    df_merged['Season'] = df_merged['Data'].apply(get_season)
    df_merged['Epoca'] = df_merged['Season']
    df_merged['Previous_Season'] = df_merged['Season'].apply(lambda x: f"{int(x.split('-')[0])-1}-{int(x.split('-')[0])}")
    
    # Calcular Jornada dinamicamente
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
        
    df_merged = df_merged.groupby('Season', group_keys=False).apply(compute_jornadas).sort_values('Data').reset_index(drop=True)
    
    # Restaurar colunas de época caso tenham sido removidas/alteradas pelo groupby
    df_merged['Season'] = df_merged['Data'].apply(get_season)
    df_merged['Epoca'] = df_merged['Season']
    df_merged['Previous_Season'] = df_merged['Season'].apply(lambda x: f"{int(x.split('-')[0])-1}-{int(x.split('-')[0])}")
    
    # Carregar base histórica de features avançadas para o lookup
    historical_lookup = {}
    cols_avancadas_order = []
    
    if os.path.exists(HISTORICAL_ADVANCED_PATH):
        print(f"Lendo base histórica para lookup: {HISTORICAL_ADVANCED_PATH}")
        df_hist = pd.read_csv(HISTORICAL_ADVANCED_PATH, encoding="latin1", low_memory=False)
        cols_avancadas_order = list(df_hist.columns)
        
        df_hist['Data'] = pd.to_datetime(df_hist['Data'], errors='coerce')
        df_hist = df_hist.dropna(subset=['Data'])
        
        # Preencher o dicionário de lookup
        for _, row in df_hist.iterrows():
            date_key = row['Data'].strftime('%Y-%m-%d')
            key = (date_key, row['Equipa_Casa'], row['Equipa_Visitante'])
            historical_lookup[key] = {
                'Casa_Elo_PreJogo': row['Casa_Elo_PreJogo'],
                'Visitante_Elo_PreJogo': row['Visitante_Elo_PreJogo'],
                'Diff_Elo': row['Diff_Elo'],
                'Casa_ExpectedGolos': row['Casa_ExpectedGolos'],
                'Visitante_ExpectedGolos': row['Visitante_ExpectedGolos'],
                'Prob_Empate_Poisson': row['Prob_Empate_Poisson'],
                'Casa_BTTS_Rate_5J': row['Casa_BTTS_Rate_5J'],
                'Visitante_BTTS_Rate_5J': row['Visitante_BTTS_Rate_5J'],
                'Casa_CleanSheet_Rate_5J': row['Casa_CleanSheet_Rate_5J'],
                'Visitante_CleanSheet_Rate_5J': row['Visitante_CleanSheet_Rate_5J'],
                'Casa_Rolling5_Remates': row['Casa_Rolling5_Remates'],
                'Visitante_Rolling5_Remates': row['Visitante_Rolling5_Remates'],
                'Casa_Rolling5_RematesAlvo': row['Casa_Rolling5_RematesAlvo'],
                'Visitante_Rolling5_RematesAlvo': row['Visitante_Rolling5_RematesAlvo'],
                'Casa_Rolling5_Cantos': row['Casa_Rolling5_Cantos'],
                'Visitante_Rolling5_Cantos': row['Visitante_Rolling5_Cantos']
            }
        print(f"Lookup histórico construído com {len(historical_lookup)} jogos.")
    else:
        print("Aviso: dataset_features_avancadas.csv original não encontrado. Todas as features serão recalculadas.")

    # 3. Listas para acumular os valores e evitar lentidão do pandas .loc
    casa_elo_list = []
    visitante_elo_list = []
    diff_elo_list = []
    casa_xg_list = []
    visitante_xg_list = []
    poisson_list = []
    casa_btts_list_out = []
    visitante_btts_list_out = []
    casa_cs_list_out = []
    visitante_cs_list_out = []
    casa_rem_list = []
    visitante_rem_list = []
    casa_rem_alvo_list = []
    visitante_rem_alvo_list = []
    casa_cantos_list = []
    visitante_cantos_list = []

    # 4. Preparar estruturas para o cálculo dinâmico cronológico
    elo_ratings = {} # team -> current elo
    
    # Dicionários de histórico dentro da época (reseta a cada época)
    team_goals_scored = {}
    team_goals_conceded = {}
    team_btts = {}
    team_cs = {}
    team_remates = {}
    team_remates_alvo = {}
    team_cantos = {}

    current_season = None

    print("Calculando features cronologicamente com carry-over e resets corretos...")
    
    for idx, row in df_merged.iterrows():
        home = row['Equipa_Casa']
        away = row['Equipa_Visitante']
        season = row['Season']
        jornada = row['Jornada']
        date_str = row['Data'].strftime('%Y-%m-%d')
        key = (date_str, home, away)
        
        # Verificar se época mudou para fazer resets de stats intra-época
        if season != current_season:
            team_goals_scored = {}
            team_goals_conceded = {}
            team_btts = {}
            team_cs = {}
            team_remates = {}
            team_remates_alvo = {}
            team_cantos = {}
            current_season = season
            
        # --- CÁLCULO ELO (Continuous across seasons) ---
        K = 20
        h_elo = elo_ratings.get(home, 1500.0)
        a_elo = elo_ratings.get(away, 1500.0)
        
        calc_casa_elo = h_elo
        calc_visi_elo = a_elo
        calc_diff_elo = h_elo - a_elo
        
        # Atualizar Elos após o jogo
        res = row['Resultado_Final']
        if res == 'H':
            S_h, S_a = 1.0, 0.0
        elif res == 'D':
            S_h, S_a = 0.5, 0.5
        else:
            S_h, S_a = 0.0, 1.0
            
        E_h = 1.0 / (1.0 + 10.0 ** ((a_elo - h_elo) / 400.0))
        E_a = 1.0 - E_h
        
        elo_ratings[home] = h_elo + K * (S_h - E_h)
        elo_ratings[away] = a_elo + K * (S_a - E_a)
        
        # --- CÁLCULO EXPECTED GOALS (xG) ---
        if jornada == 1:
            h_att = row['Home_hist_GolosMarcados'] / row['Home_hist_JogosDisputados'] if not pd.isna(row['Home_hist_JogosDisputados']) else 1.3
            a_def = row['Away_hist_GolosSofridos'] / row['Away_hist_JogosDisputados'] if not pd.isna(row['Away_hist_JogosDisputados']) else 1.1
            a_att = row['Away_hist_GolosMarcados'] / row['Away_hist_JogosDisputados'] if not pd.isna(row['Away_hist_JogosDisputados']) else 1.1
            h_def = row['Home_hist_GolosSofridos'] / row['Home_hist_JogosDisputados'] if not pd.isna(row['Home_hist_JogosDisputados']) else 1.3
            
            calc_casa_xg = (h_att + a_def) / 2.0
            calc_visi_xg = (a_att + h_def) / 2.0
        else:
            h_scored = team_goals_scored.get(home, [])
            h_conceded = team_goals_conceded.get(home, [])
            a_scored = team_goals_scored.get(away, [])
            a_conceded = team_goals_conceded.get(away, [])
            
            w_h = min(len(h_scored), 10)
            w_a = min(len(a_scored), 10)
            
            h_avg_scored = sum(h_scored[-w_h:]) / w_h if w_h > 0 else 1.3
            h_avg_conceded = sum(h_conceded[-w_h:]) / w_h if w_h > 0 else 1.3
            a_avg_scored = sum(a_scored[-w_a:]) / w_a if w_a > 0 else 1.1
            a_avg_conceded = sum(a_conceded[-w_a:]) / w_a if w_a > 0 else 1.1
            
            calc_casa_xg = (h_avg_scored + a_avg_conceded) / 2.0
            calc_visi_xg = (a_avg_scored + h_avg_conceded) / 2.0
            
        # Atualizar histórico de golos
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
        
        # --- CÁLCULO POISSON ---
        def compute_poisson_draw(l1, l2):
            if pd.isna(l1) or pd.isna(l2):
                return np.nan
            return sum(poisson.pmf(k, l1) * poisson.pmf(k, l2) for k in range(50))
            
        calc_poisson = compute_poisson_draw(calc_casa_xg, calc_visi_xg)
        
        # --- CÁLCULO BTTS E CLEAN SHEET RATES ---
        h_btts_list = team_btts.get(home, [])
        a_btts_list = team_btts.get(away, [])
        
        w_btts_h = min(len(h_btts_list), 5)
        w_btts_a = min(len(a_btts_list), 5)
        
        calc_casa_btts = sum(h_btts_list[-w_btts_h:]) / w_btts_h if w_btts_h > 0 else 0.5
        calc_visi_btts = sum(a_btts_list[-w_btts_a:]) / w_btts_a if w_btts_a > 0 else 0.5
        
        h_cs_list = team_cs.get(home, [])
        a_cs_list = team_cs.get(away, [])
        
        w_cs_h = min(len(h_cs_list), 5)
        w_cs_a = min(len(a_cs_list), 5)
        
        calc_casa_cs = sum(h_cs_list[-w_cs_h:]) / w_cs_h if w_cs_h > 0 else 0.3
        calc_visi_cs = sum(a_cs_list[-w_cs_a:]) / w_cs_a if w_cs_a > 0 else 0.3
        
        # Atualizar histórico de BTTS e CS
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
        
        # --- CÁLCULO ROLLING SHOTS, REMATES ALVO E CANTOS ---
        h_rem = team_remates.get(home, [])
        a_rem = team_remates.get(away, [])
        h_rem_alvo = team_remates_alvo.get(home, [])
        a_rem_alvo = team_remates_alvo.get(away, [])
        h_can = team_cantos.get(home, [])
        a_can = team_cantos.get(away, [])
        
        w_rem_h = min(len(h_rem), 5)
        w_rem_a = min(len(a_rem), 5)
        
        calc_casa_rem = sum(h_rem[-w_rem_h:]) / w_rem_h if w_rem_h > 0 else np.nan
        calc_casa_rem_alvo = sum(h_rem_alvo[-w_rem_h:]) / w_rem_h if w_rem_h > 0 else np.nan
        calc_casa_cantos = sum(h_can[-w_rem_h:]) / w_rem_h if w_rem_h > 0 else np.nan
        
        calc_visi_rem = sum(a_rem[-w_rem_a:]) / w_rem_a if w_rem_a > 0 else np.nan
        calc_visi_rem_alvo = sum(a_rem_alvo[-w_rem_a:]) / w_rem_a if w_rem_a > 0 else np.nan
        calc_visi_cantos = sum(a_can[-w_rem_a:]) / w_rem_a if w_rem_a > 0 else np.nan
        
        # Atualizar histórico de remates e cantos
        team_remates[home].append(row['Remates_Casa'] if not pd.isna(row['Remates_Casa']) else np.nan)
        team_remates_alvo[home].append(row['Remates_Alvo_Casa'] if not pd.isna(row['Remates_Alvo_Casa']) else np.nan)
        team_cantos[home].append(row['Cantos_Casa'] if not pd.isna(row['Cantos_Casa']) else np.nan)
        
        team_remates[away].append(row['Remates_Visitante'] if not pd.isna(row['Remates_Visitante']) else np.nan)
        team_remates_alvo[away].append(row['Remates_Alvo_Visitante'] if not pd.isna(row['Remates_Alvo_Visitante']) else np.nan)
        team_cantos[away].append(row['Cantos_Visitante'] if not pd.isna(row['Cantos_Visitante']) else np.nan)
        
        # --- APLICAR MODO HÍBRIDO (LOOKUP VS CALCULADO) ---
        if key in historical_lookup:
            orig = historical_lookup[key]
            casa_elo_list.append(orig['Casa_Elo_PreJogo'])
            visitante_elo_list.append(orig['Visitante_Elo_PreJogo'])
            diff_elo_list.append(orig['Diff_Elo'])
            casa_xg_list.append(orig['Casa_ExpectedGolos'])
            visitante_xg_list.append(orig['Visitante_ExpectedGolos'])
            poisson_list.append(orig['Prob_Empate_Poisson'])
            casa_btts_list_out.append(orig['Casa_BTTS_Rate_5J'])
            visitante_btts_list_out.append(orig['Visitante_BTTS_Rate_5J'])
            casa_cs_list_out.append(orig['Casa_CleanSheet_Rate_5J'])
            visitante_cs_list_out.append(orig['Visitante_CleanSheet_Rate_5J'])
            casa_rem_list.append(orig['Casa_Rolling5_Remates'])
            visitante_rem_list.append(orig['Visitante_Rolling5_Remates'])
            casa_rem_alvo_list.append(orig['Casa_Rolling5_RematesAlvo'])
            visitante_rem_alvo_list.append(orig['Visitante_Rolling5_RematesAlvo'])
            casa_cantos_list.append(orig['Casa_Rolling5_Cantos'])
            visitante_cantos_list.append(orig['Visitante_Rolling5_Cantos'])
        else:
            casa_elo_list.append(calc_casa_elo)
            visitante_elo_list.append(calc_visi_elo)
            diff_elo_list.append(calc_diff_elo)
            casa_xg_list.append(calc_casa_xg)
            visitante_xg_list.append(calc_visi_xg)
            poisson_list.append(calc_poisson)
            casa_btts_list_out.append(calc_casa_btts)
            visitante_btts_list_out.append(calc_visi_btts)
            casa_cs_list_out.append(calc_casa_cs)
            visitante_cs_list_out.append(calc_visi_cs)
            casa_rem_list.append(calc_casa_rem)
            visitante_rem_list.append(calc_visi_rem)
            casa_rem_alvo_list.append(calc_casa_rem_alvo)
            visitante_rem_alvo_list.append(calc_visi_rem_alvo)
            casa_cantos_list.append(calc_casa_cantos)
            visitante_cantos_list.append(calc_visi_cantos)

    # 5. Atribuir os valores calculados de volta ao DataFrame (Operação instantânea)
    print("Atribuindo colunas de forma otimizada...")
    df_merged['Casa_Elo_PreJogo'] = casa_elo_list
    df_merged['Visitante_Elo_PreJogo'] = visitante_elo_list
    df_merged['Diff_Elo'] = diff_elo_list
    df_merged['Casa_ExpectedGolos'] = casa_xg_list
    df_merged['Visitante_ExpectedGolos'] = visitante_xg_list
    df_merged['Prob_Empate_Poisson'] = poisson_list
    df_merged['Casa_BTTS_Rate_5J'] = casa_btts_list_out
    df_merged['Visitante_BTTS_Rate_5J'] = visitante_btts_list_out
    df_merged['Casa_CleanSheet_Rate_5J'] = casa_cs_list_out
    df_merged['Visitante_CleanSheet_Rate_5J'] = visitante_cs_list_out
    df_merged['Casa_Rolling5_Remates'] = casa_rem_list
    df_merged['Visitante_Rolling5_Remates'] = visitante_rem_list
    df_merged['Casa_Rolling5_RematesAlvo'] = casa_rem_alvo_list
    df_merged['Visitante_Rolling5_RematesAlvo'] = visitante_rem_alvo_list
    df_merged['Casa_Rolling5_Cantos'] = casa_cantos_list
    df_merged['Visitante_Rolling5_Cantos'] = visitante_cantos_list

    # 6. Gravar de volta no ficheiro mesclado v2
    print(f"Gravando {TARGET_MERGED_PATH} atualizado em 'latin1'...")
    df_merged['Data'] = df_merged['Data'].dt.strftime('%Y-%m-%d')
    df_merged.to_csv(TARGET_MERGED_PATH, index=False, encoding='latin1')
    
    # 7. Gravar de volta no ficheiro de features avançadas com schema e colunas corretas
    if cols_avancadas_order:
        print(f"Gravando {HISTORICAL_ADVANCED_PATH} atualizado em 'latin1'...")
        df_avancadas_save = df_merged[[c for c in cols_avancadas_order if c in df_merged.columns]].copy()
        
        missing_cols = [c for c in cols_avancadas_order if c not in df_merged.columns]
        if missing_cols:
            print(f"Aviso: Colunas originais em falta no merge: {missing_cols}")
            
        df_avancadas_save.to_csv(HISTORICAL_ADVANCED_PATH, index=False, encoding='latin1')
    else:
        print(f"Como não tínhamos o layout original, criando novo em {HISTORICAL_ADVANCED_PATH}")
        df_merged.to_csv(HISTORICAL_ADVANCED_PATH, index=False, encoding='latin1')
        
    print("=" * 60)
    print("FEATURES AVANÇADAS ATUALIZADAS E SINCRONIZADAS COM SUCESSO!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    update_advanced_datasets()
