"""
Monte Carlo Simulation Engine — Refatorado para uso como módulo importável.

Baseado no script original Notebooks/Simulacao_MonteCarlo.py.
Toda a lógica de impressão foi substituída por retorno de dicionários estruturados.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import time
import os
import warnings

warnings.filterwarnings("ignore")

# Path para o dataset (relativo à raiz do projeto)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, "Datasets", "dataset_features_avancadas.csv")

# Features usadas pelo modelo (idênticas ao script original)
FEATURES = [
    "Home_hist_Pontos", "Home_hist_GolosMarcados", "Home_hist_GolosSofridos",
    "Home_hist_DiferençaDeGolos", "Home_hist_Vitórias", "Home_hist_Derrotas", "Home_hist_Empates",
    "Away_hist_Pontos", "Away_hist_GolosMarcados", "Away_hist_GolosSofridos",
    "Away_hist_DiferençaDeGolos", "Away_hist_Vitórias", "Away_hist_Derrotas", "Away_hist_Empates",

    "Casa_Form_Pts5", "Casa_Form_GM5", "Casa_Form_GS5",
    "Visitante_Form_Pts5", "Visitante_Form_GM5", "Visitante_Form_GS5",
    "Casa_Form_Empates5", "Visitante_Form_Empates5",

    "Home_hist_GolosEsperados", "Home_hist_GolosEsperadosSofridos",
    "Away_hist_GolosEsperados", "Away_hist_GolosEsperadosSofridos",
    "Home_hist_PosseDeBola", "Away_hist_PosseDeBola",
    "Home_hist_PassesProgressivos", "Away_hist_PassesProgressivos",
    "Home_hist_JogosSemSofrerGolos", "Away_hist_JogosSemSofrerGolos",

    "Casa_Elo_PreJogo", "Visitante_Elo_PreJogo", "Diff_Elo",
    "Casa_ExpectedGolos", "Visitante_ExpectedGolos", "Prob_Empate_Poisson",
    "Casa_BTTS_Rate_5J", "Visitante_BTTS_Rate_5J",
    "Casa_CleanSheet_Rate_5J", "Visitante_CleanSheet_Rate_5J",
    "Casa_Rolling5_Remates", "Visitante_Rolling5_Remates",
    "Casa_Rolling5_RematesAlvo", "Visitante_Rolling5_RematesAlvo",
    "Casa_Rolling5_Cantos", "Visitante_Rolling5_Cantos",

    "Jornada"
]

# Features que dependem dos últimos 5 jogos (rolling window).
# Nas primeiras jornadas, estes valores vêm da época anterior e devem ter peso reduzido.
ROLLING_FEATURES = [
    "Casa_Form_Pts5", "Casa_Form_GM5", "Casa_Form_GS5",
    "Visitante_Form_Pts5", "Visitante_Form_GM5", "Visitante_Form_GS5",
    "Casa_Form_Empates5", "Visitante_Form_Empates5",
    "Casa_BTTS_Rate_5J", "Visitante_BTTS_Rate_5J",
    "Casa_CleanSheet_Rate_5J", "Visitante_CleanSheet_Rate_5J",
    "Casa_Rolling5_Remates", "Visitante_Rolling5_Remates",
    "Casa_Rolling5_RematesAlvo", "Visitante_Rolling5_RematesAlvo",
    "Casa_Rolling5_Cantos", "Visitante_Rolling5_Cantos",
]

# Mapeamento de nomes técnicos para labels legíveis em Português
FEATURE_LABELS = {
    "Home_hist_Pontos": "Pontos Históricos (Casa)",
    "Home_hist_GolosMarcados": "Golos Marcados Históricos (Casa)",
    "Home_hist_GolosSofridos": "Golos Sofridos Históricos (Casa)",
    "Home_hist_DiferençaDeGolos": "Diferença de Golos (Casa)",
    "Home_hist_Vitórias": "Vitórias Históricas (Casa)",
    "Home_hist_Derrotas": "Derrotas Históricas (Casa)",
    "Home_hist_Empates": "Empates Históricos (Casa)",
    "Away_hist_Pontos": "Pontos Históricos (Fora)",
    "Away_hist_GolosMarcados": "Golos Marcados Históricos (Fora)",
    "Away_hist_GolosSofridos": "Golos Sofridos Históricos (Fora)",
    "Away_hist_DiferençaDeGolos": "Diferença de Golos (Fora)",
    "Away_hist_Vitórias": "Vitórias Históricas (Fora)",
    "Away_hist_Derrotas": "Derrotas Históricas (Fora)",
    "Away_hist_Empates": "Empates Históricos (Fora)",
    "Casa_Form_Pts5": "Pontos Últimos 5 Jogos (Casa)",
    "Casa_Form_GM5": "Golos Marcados Últimos 5J (Casa)",
    "Casa_Form_GS5": "Golos Sofridos Últimos 5J (Casa)",
    "Visitante_Form_Pts5": "Pontos Últimos 5 Jogos (Fora)",
    "Visitante_Form_GM5": "Golos Marcados Últimos 5J (Fora)",
    "Visitante_Form_GS5": "Golos Sofridos Últimos 5J (Fora)",
    "Casa_Form_Empates5": "Empates Últimos 5 Jogos (Casa)",
    "Visitante_Form_Empates5": "Empates Últimos 5 Jogos (Fora)",
    "Home_hist_GolosEsperados": "Golos Esperados xG (Casa)",
    "Home_hist_GolosEsperadosSofridos": "xG Sofridos (Casa)",
    "Away_hist_GolosEsperados": "Golos Esperados xG (Fora)",
    "Away_hist_GolosEsperadosSofridos": "xG Sofridos (Fora)",
    "Home_hist_PosseDeBola": "Posse de Bola (Casa)",
    "Away_hist_PosseDeBola": "Posse de Bola (Fora)",
    "Home_hist_PassesProgressivos": "Passes Progressivos (Casa)",
    "Away_hist_PassesProgressivos": "Passes Progressivos (Fora)",
    "Home_hist_JogosSemSofrerGolos": "Clean Sheets (Casa)",
    "Away_hist_JogosSemSofrerGolos": "Clean Sheets (Fora)",
    "Casa_Elo_PreJogo": "Rating Elo (Casa)",
    "Visitante_Elo_PreJogo": "Rating Elo (Fora)",
    "Diff_Elo": "Diferença de Elo entre Equipas",
    "Casa_ExpectedGolos": "Golos Esperados Poisson (Casa)",
    "Visitante_ExpectedGolos": "Golos Esperados Poisson (Fora)",
    "Prob_Empate_Poisson": "Probabilidade de Empate (Poisson)",
    "Casa_BTTS_Rate_5J": "Ambas Marcam % Últimos 5J (Casa)",
    "Visitante_BTTS_Rate_5J": "Ambas Marcam % Últimos 5J (Fora)",
    "Casa_CleanSheet_Rate_5J": "Baliza a Zeros % Últimos 5J (Casa)",
    "Visitante_CleanSheet_Rate_5J": "Baliza a Zeros % Últimos 5J (Fora)",
    "Casa_Rolling5_Remates": "Média Remates Últimos 5J (Casa)",
    "Visitante_Rolling5_Remates": "Média Remates Últimos 5J (Fora)",
    "Casa_Rolling5_RematesAlvo": "Remates à Baliza Últimos 5J (Casa)",
    "Visitante_Rolling5_RematesAlvo": "Remates à Baliza Últimos 5J (Fora)",
    "Casa_Rolling5_Cantos": "Média Cantos Últimos 5J (Casa)",
    "Visitante_Rolling5_Cantos": "Média Cantos Últimos 5J (Fora)",
    "Jornada": "Número da Jornada",
}


def load_and_prepare_data():
    """Carrega e prepara o dataset com Epoca e Jornada."""
    df = pd.read_csv(DATASET_PATH, low_memory=False)

    if "Data" in df.columns:
        df["Data"] = pd.to_datetime(df["Data"], dayfirst=True, errors="coerce")
        df = df.dropna(subset=["Data"]).sort_values("Data").reset_index(drop=True)

        # Criar coluna Epoca se não existir
        if "Epoca" not in df.columns:
            def get_season(date):
                return f"{date.year}-{date.year+1}" if date.month >= 7 else f"{date.year-1}-{date.year}"
            df["Epoca"] = df["Data"].apply(get_season)

        # Criar Jornada se não existir
        if "Jornada" not in df.columns:
            def compute_jornadas(season_df):
                season_df = season_df.copy()
                team_games = {}
                jornadas = []
                for idx, row in season_df.iterrows():
                    home, away = row["Equipa_Casa"], row["Equipa_Visitante"]
                    hg, ag = team_games.get(home, 0), team_games.get(away, 0)
                    matchday = max(hg, ag) + 1
                    jornadas.append(matchday)
                    team_games[home] = hg + 1
                    team_games[away] = ag + 1
                season_df["Jornada"] = jornadas
                return season_df
            df = df.groupby("Epoca", group_keys=False).apply(compute_jornadas).sort_values("Data").reset_index(drop=True)

    return df


def apply_feature_decay(df):
    """
    Aplica Feature Decay às features rolling baseado na jornada.

    Nas primeiras jornadas da época, as features dos 'últimos 5 jogos' contêm
    dados da época anterior (cruzam épocas). Para evitar que o modelo confie
    nestes valores desatualizados, multiplicamos por um fator de confiança:

        fator = min((jornada - 1) / 5, 1.0)

    - Jornada 1: fator = 0.0 → rolling features a zero (modelo usa Elo + hist_)
    - Jornada 2: fator = 0.2 → 20% do peso
    - Jornada 3: fator = 0.4 → 40% do peso
    - Jornada 6+: fator = 1.0 → peso total (5+ jogos da época atual)
    """
    df = df.copy()
    if "Jornada" in df.columns:
        fator = ((df["Jornada"] - 1) / 5).clip(upper=1.0)
        for col in ROLLING_FEATURES:
            if col in df.columns:
                df[col] = df[col] * fator
    return df


def get_info():
    """Retorna informação sobre os dados disponíveis para o frontend."""
    df = load_and_prepare_data()
    df = df.dropna(subset=FEATURES).copy()

    # Época de teste: 2023-2024
    df_test = df[df["Epoca"] == "2023-2024"]
    equipas = sorted(df_test["Equipa_Casa"].unique().tolist())
    jornada_min = int(df_test["Jornada"].min())
    jornada_max = int(df_test["Jornada"].max())

    return {
        "epoca_teste": "2023-2024",
        "equipas": equipas,
        "jornada_min": jornada_min,
        "jornada_max": jornada_max,
        "total_jogos_dataset": len(df),
        "features_utilizadas": len(FEATURES)
    }


def run_simulation(jornada_alvo: int, num_simulacoes: int = 1000):
    """
    Executa a simulação Monte Carlo e retorna os resultados como dicionário.

    Args:
        jornada_alvo: Jornada a partir da qual começa a simulação
        num_simulacoes: Número de iterações Monte Carlo

    Returns:
        Dicionário com resultados estruturados
    """
    start_time = time.time()

    df = load_and_prepare_data()
    df = df.dropna(subset=FEATURES).copy()

    # Preparar Target
    le = LabelEncoder()
    df["Target"] = le.fit_transform(df["Resultado_Final"])

    # 1. Separar dados de treino (antes de 23/24) e teste (época 23/24)
    df_train = df[df["Epoca"] != "2023-2024"].copy()
    df_test = df[df["Epoca"] == "2023-2024"].copy()

    # 2. Congelamento do Estado Real
    jogos_passados = df_test[df_test["Jornada"] < jornada_alvo]
    jogos_futuros = df_test[df_test["Jornada"] >= jornada_alvo]

    if jogos_futuros.empty:
        return {"error": f"Não há jogos futuros a partir da jornada {jornada_alvo}."}

    # Rollout Temporal
    df_train = pd.concat([df_train, jogos_passados], ignore_index=True)

    # Aplicar Feature Decay — reduzir peso das rolling features nas primeiras jornadas
    df_train = apply_feature_decay(df_train)

    # Treinar modelo
    rf_model = RandomForestClassifier(
        n_estimators=100, max_depth=10, class_weight="balanced", random_state=42, n_jobs=-1
    )
    rf_model.fit(df_train[FEATURES], df_train["Target"])

    equipas = sorted(df_test["Equipa_Casa"].unique().tolist())
    tabela_real = {eq: 0 for eq in equipas}

    # Calcular pontos reais (jogos já disputados)
    for _, row in jogos_passados.iterrows():
        res_real = le.classes_[row["Target"]]
        if res_real == "H":
            tabela_real[row["Equipa_Casa"]] += 3
        elif res_real == "A":
            tabela_real[row["Equipa_Visitante"]] += 3
        elif res_real == "D":
            tabela_real[row["Equipa_Casa"]] += 1
            tabela_real[row["Equipa_Visitante"]] += 1

    # 3. Simulação de Monte Carlo
    campeoes_contagem = {eq: 0 for eq in equipas}

    # Aplicar Feature Decay aos jogos futuros (consistente com treino)
    jogos_futuros_decayed = apply_feature_decay(jogos_futuros)
    X_futuro = jogos_futuros_decayed[FEATURES]
    probabilidades_futuro = rf_model.predict_proba(X_futuro)
    classes_modelo = le.classes_

    # Calcular fator de confiança para informação do frontend
    jogos_na_epoca = max(jornada_alvo - 1, 0)
    fator_confianca = min(jogos_na_epoca / 5, 1.0)
    decay_ativo = fator_confianca < 1.0

    for i in range(num_simulacoes):
        tabela_simulada = tabela_real.copy()

        for idx_jogo, (_, row) in enumerate(jogos_futuros.iterrows()):
            probs_jogo = probabilidades_futuro[idx_jogo]
            res_simulado = np.random.choice(classes_modelo, p=probs_jogo)

            if res_simulado == "H":
                tabela_simulada[row["Equipa_Casa"]] += 3
            elif res_simulado == "A":
                tabela_simulada[row["Equipa_Visitante"]] += 3
            elif res_simulado == "D":
                tabela_simulada[row["Equipa_Casa"]] += 1
                tabela_simulada[row["Equipa_Visitante"]] += 1

        classificacao_final = sorted(tabela_simulada.items(), key=lambda x: x[1], reverse=True)
        campeao = classificacao_final[0][0]
        campeoes_contagem[campeao] += 1

    # 4. Montar resultados
    elapsed = round(time.time() - start_time, 2)

    # Probabilidades de título (ordenadas por probabilidade decrescente)
    probabilidades_titulo = {}
    for equipa, vitorias in sorted(campeoes_contagem.items(), key=lambda x: x[1], reverse=True):
        probabilidades_titulo[equipa] = round((vitorias / num_simulacoes) * 100, 2)

    # Tabela real (ordenada por pontos)
    tabela_real_sorted = dict(sorted(tabela_real.items(), key=lambda x: x[1], reverse=True))

    # Detalhes dos jogos futuros para contexto
    jogos_futuros_lista = []
    for idx_jogo, (_, row) in enumerate(jogos_futuros.iterrows()):
        probs = probabilidades_futuro[idx_jogo]
        jogo = {
            "casa": row["Equipa_Casa"],
            "fora": row["Equipa_Visitante"],
            "jornada": int(row["Jornada"]),
            "prob_casa": round(float(probs[list(classes_modelo).index("H")]) * 100, 1) if "H" in classes_modelo else 0,
            "prob_empate": round(float(probs[list(classes_modelo).index("D")]) * 100, 1) if "D" in classes_modelo else 0,
            "prob_fora": round(float(probs[list(classes_modelo).index("A")]) * 100, 1) if "A" in classes_modelo else 0,
        }
        jogos_futuros_lista.append(jogo)

    # 5. Feature Importance (Top 15)
    importances = rf_model.feature_importances_
    feat_imp = sorted(zip(FEATURES, importances), key=lambda x: x[1], reverse=True)
    total_importance = sum(importances)
    feature_importance = []
    for feat_name, imp in feat_imp[:15]:
        label = FEATURE_LABELS.get(feat_name, feat_name)
        pct = round((imp / total_importance) * 100, 2)
        feature_importance.append({
            "feature": feat_name,
            "label": label,
            "importancia": pct
        })

    return {
        "jornada": jornada_alvo,
        "num_simulacoes": num_simulacoes,
        "tempo_execucao": elapsed,
        "jogos_treino": len(df_train),
        "jogos_futuros": len(jogos_futuros),
        "jornadas_simuladas": f"{jornada_alvo}\u2013{int(jogos_futuros['Jornada'].max())}",
        "tabela_real": tabela_real_sorted,
        "probabilidades_titulo": probabilidades_titulo,
        "proximos_jogos": jogos_futuros_lista[:9],  # Primeiros 9 jogos (1 jornada)
        "feature_importance": feature_importance,
        "feature_decay": {
            "ativo": decay_ativo,
            "fator_confianca": round(fator_confianca * 100),
            "jogos_na_epoca": jogos_na_epoca,
            "descricao": (
                f"Features rolling com {round(fator_confianca * 100)}% de peso "
                f"({jogos_na_epoca}/5 jogos na época)"
            ) if decay_ativo else "Features rolling com peso total"
        },
    }

