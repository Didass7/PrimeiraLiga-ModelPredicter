"""
Monte Carlo Simulation Engine — Refatorado para uso como módulo importável.

Baseado no script original Notebooks/Simulacao_MonteCarlo.py.
Toda a lógica de impressão foi substituída por retorno de dicionários estruturados.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from sklearn.utils.class_weight import compute_sample_weight
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


def fix_mojibake(text):
    """Corrige strings com encodings mistos (UTF-8 decodificado incorretamente como Latin-1)."""
    if not isinstance(text, str):
        return text
    try:
        return text.encode('latin-1').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text


def load_and_prepare_data():
    """Carrega e prepara o dataset com Epoca e Jornada."""
    df = pd.read_csv(DATASET_PATH, encoding='latin1', low_memory=False)

    # Corrigir mojibake/encoding misto nos nomes das colunas
    df.columns = [fix_mojibake(col) for col in df.columns]

    # Corrigir mojibake/encoding misto em todas as colunas de texto
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].apply(fix_mojibake)

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

    # Obter todas as épocas disponíveis ordenadas cronologicamente
    epocas = sorted(df["Epoca"].dropna().unique().tolist())

    # Montar informação detalhada para cada época disponível
    detalhes_epocas = {}
    for ep in epocas:
        df_ep = df[df["Epoca"] == ep]
        equipas_ep = sorted(df_ep["Equipa_Casa"].unique().tolist())
        if not equipas_ep:
            continue
        
        jornada_min = int(df_ep["Jornada"].min())
        jornada_max = int(df_ep["Jornada"].max())
        
        detalhes_epocas[ep] = {
            "equipas": equipas_ep,
            "jornada_min": jornada_min,
            "jornada_max": jornada_max,
            "total_jogos": len(df_ep)
        }

    # Definir como época default a mais recente que tenha jogos
    epoca_default = epocas[-1] if epocas else "2023-2024"

    return {
        "epocas": epocas,
        "detalhes_epocas": detalhes_epocas,
        "epoca_default": epoca_default,
        "total_jogos_dataset": len(df),
        "features_utilizadas": len(FEATURES)
    }


def run_simulation(jornada_alvo: int, num_simulacoes: int = 1000, epoca_alvo: str = "2023-2024", modelo_alvo: str = "Random Forest"):
    """
    Executa a simulação Monte Carlo e retorna os resultados como dicionário.

    Args:
        jornada_alvo: Jornada a partir da qual começa a simulação
        num_simulacoes: Número de iterações Monte Carlo
        epoca_alvo: A época a simular (ex: '2024-2025')

    Returns:
        Dicionário com resultados estruturados
    """
    start_time = time.time()

    df = load_and_prepare_data()
    df = df.dropna(subset=FEATURES).copy()

    # Garantir que a época alvo existe no dataset
    if epoca_alvo not in df["Epoca"].values:
        return {"error": f"Época {epoca_alvo} não encontrada no dataset."}

    # Preparar Target
    le = LabelEncoder()
    df["Target"] = le.fit_transform(df["Resultado_Final"])

    # 1. Separar dados de treino (excluindo a época alvo) e teste (época alvo)
    df_train = df[df["Epoca"] != epoca_alvo].copy()
    df_test = df[df["Epoca"] == epoca_alvo].copy()

    # 2. Congelamento do Estado Real
    jogos_passados = df_test[df_test["Jornada"] < jornada_alvo]
    jogos_futuros = df_test[df_test["Jornada"] >= jornada_alvo]

    if jogos_futuros.empty:
        return {"error": f"Não há jogos futuros a partir da jornada {jornada_alvo}."}

    # Rollout Temporal
    df_train = pd.concat([df_train, jogos_passados], ignore_index=True)

    # Aplicar Feature Decay — reduzir peso das rolling features nas primeiras jornadas
    df_train = apply_feature_decay(df_train)

    # 2. Treinar o modelo de Machine Learning selecionado
    if modelo_alvo == "XGBoost":
        model = XGBClassifier(
            objective='multi:softprob',
            num_class=3,
            n_estimators=100,
            learning_rate=0.05,
            max_depth=4,
            random_state=42,
            eval_metric='mlogloss',
            n_jobs=-1
        )
        sample_weights = compute_sample_weight(
            class_weight='balanced',
            y=df_train["Target"]
        )
        model.fit(df_train[FEATURES], df_train["Target"], sample_weight=sample_weights)
    elif modelo_alvo == "Decision Tree":
        model = DecisionTreeClassifier(
            max_depth=4,
            class_weight='balanced',
            random_state=42
        )
        model.fit(df_train[FEATURES], df_train["Target"])
    elif modelo_alvo == "Logistic Regression":
        model = LogisticRegression(
            solver='lbfgs',
            max_iter=1000,
            random_state=42,
            class_weight='balanced'
        )
        model.fit(df_train[FEATURES], df_train["Target"])
    else:
        # Default: Random Forest
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=4,
            min_samples_leaf=8,
            min_samples_split=10,
            max_features=0.2,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1
        )
        model.fit(df_train[FEATURES], df_train["Target"])

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
    probabilidades_futuro = model.predict_proba(X_futuro)
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

    # 5. Calcular Métricas de Validação no Passado (Accuracy & Recall)
    metricas_previsao = {
        "disponivel": False,
        "accuracy": 0.0,
        "jogos_avaliados": 0,
        "recall": {
            "H": 0.0,
            "D": 0.0,
            "A": 0.0
        },
        "detalhes": {}
    }

    if not jogos_passados.empty:
        try:
            # Para evitar Data Leakage (Treino vs Teste), treinamos um modelo de validação auxiliar (model_val)
            # EXCLUINDO os jogos passados da época atual que serão usados para calcular as métricas.
            df_train_val = df[df["Epoca"] != epoca_alvo].copy()
            df_train_val = apply_feature_decay(df_train_val)

            if modelo_alvo == "XGBoost":
                model_val = XGBClassifier(
                    objective='multi:softprob',
                    num_class=3,
                    n_estimators=100,
                    learning_rate=0.05,
                    max_depth=4,
                    random_state=42,
                    eval_metric='mlogloss',
                    n_jobs=-1
                )
                sample_weights_val = compute_sample_weight(
                    class_weight='balanced',
                    y=df_train_val["Target"]
                )
                model_val.fit(df_train_val[FEATURES], df_train_val["Target"], sample_weight=sample_weights_val)
            elif modelo_alvo == "Decision Tree":
                model_val = DecisionTreeClassifier(
                    max_depth=4,
                    class_weight='balanced',
                    random_state=42
                )
                model_val.fit(df_train_val[FEATURES], df_train_val["Target"])
            elif modelo_alvo == "Logistic Regression":
                model_val = LogisticRegression(
                    solver='lbfgs',
                    max_iter=1000,
                    random_state=42,
                    class_weight='balanced'
                )
                model_val.fit(df_train_val[FEATURES], df_train_val["Target"])
            else:
                model_val = RandomForestClassifier(
                    n_estimators=100,
                    max_depth=4,
                    min_samples_leaf=8,
                    min_samples_split=10,
                    max_features=0.2,
                    class_weight="balanced",
                    random_state=42,
                    n_jobs=-1
                )
                model_val.fit(df_train_val[FEATURES], df_train_val["Target"])

            # Selecionar features e target dos jogos passados
            X_passado = apply_feature_decay(jogos_passados)[FEATURES]
            y_passado = jogos_passados["Target"].values
            
            # Fazer previsões com o modelo de validação out-of-sample (sem leakage)
            preds_passados = model_val.predict(X_passado)
            
            # Accuracy Geral
            accuracy_geral = float(np.mean(preds_passados == y_passado))
            
            # Mapeamento de classes e cálculo de Recall
            classes_nome = {
                "H": "Vitórias em Casa (H)",
                "D": "Empates (D)",
                "A": "Vitórias Fora (A)"
            }
            
            recall_por_classe = {}
            for idx, class_label in enumerate(le.classes_):
                nome = classes_nome.get(class_label, class_label)
                reais_classe = (y_passado == idx)
                total_reais = int(np.sum(reais_classe))
                
                if total_reais > 0:
                    acertos_classe = int(np.sum((preds_passados == idx) & reais_classe))
                    recall_val = float(acertos_classe / total_reais)
                else:
                    recall_val = 0.0
                    
                recall_por_classe[class_label] = {
                    "label": nome,
                    "val": round(recall_val * 100, 1),
                    "reais": total_reais,
                    "previstos": int(np.sum(preds_passados == idx))
                }
                
            metricas_previsao = {
                "disponivel": True,
                "accuracy": round(accuracy_geral * 100, 1),
                "jogos_avaliados": len(jogos_passados),
                "recall": {
                    "H": recall_por_classe.get("H", {}).get("val", 0.0),
                    "D": recall_por_classe.get("D", {}).get("val", 0.0),
                    "A": recall_por_classe.get("A", {}).get("val", 0.0)
                },
                "detalhes": recall_por_classe
            }
        except Exception as e:
            print(f"Erro ao calcular métricas de validação: {e}")
 
    # 6. Feature Importance (Top 15)
    if modelo_alvo == "Logistic Regression":
        importances = np.mean(np.abs(model.coef_), axis=0)
    else:
        importances = model.feature_importances_
        
    feat_imp = sorted(zip(FEATURES, importances), key=lambda x: x[1], reverse=True)
    total_importance = sum(importances)
    feature_importance = []
    for feat_name, imp in feat_imp[:15]:
        label = FEATURE_LABELS.get(feat_name, feat_name)
        pct = round(float(imp / total_importance) * 100, 2) if total_importance > 0 else 0.0
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
        "jornadas_simuladas": f"{jornada_alvo}–{int(jogos_futuros['Jornada'].max())}",
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
        "metricas_previsao": metricas_previsao,
    }

