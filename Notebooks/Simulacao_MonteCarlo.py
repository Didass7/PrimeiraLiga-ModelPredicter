import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import argparse
import warnings

warnings.filterwarnings("ignore")

def load_and_prepare_data():
    try:
        df = pd.read_csv(r"d:\Diogo\Ambiente de Trabalho\PROJETO\Datasets\dataset_features_avancadas.csv", low_memory=False)
        print("Dataset carregado com sucesso!")
    except FileNotFoundError:
        print("Erro: Ficheiro não encontrado. Verifica o caminho.")
        return None

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

def main(jornada_alvo, num_simulacoes=1000):
    df = load_and_prepare_data()
    if df is None: return

    # Limpar NAs nas features
    df = df.dropna(subset=FEATURES).copy()
    
    # Preparar Target
    le = LabelEncoder()
    df["Target"] = le.fit_transform(df["Resultado_Final"])
    
    # 1. Separar dados de treino (antes de 23/24) e teste (época 23/24)
    df_train = df[df["Epoca"] != "2023-2024"].copy()
    df_test = df[df["Epoca"] == "2023-2024"].copy()
    
    # 2. Congelamento do Estado Real: Extrair os jogos da atual época vs. futuro
    jogos_passados = df_test[df_test["Jornada"] < jornada_alvo]
    jogos_futuros = df_test[df_test["Jornada"] >= jornada_alvo]
    
    if jogos_futuros.empty:
        print(f"Não há jogos futuros a partir da jornada {jornada_alvo}.")
        return

    # Rollout Temporal: o treino passa a incluir todos os jogos passados da nova época!
    df_train = pd.concat([df_train, jogos_passados], ignore_index=True)
    
    print(f"Treino: {len(df_train)} jogos (Histórico + época atual) | Teste: {len(jogos_futuros)} jogos restantes")
    
    # Treinar modelo (agora sabe o que aconteceu durante a época até à jornada atual)
    print("A treinar modelo Random Forest...")
    rf_model = RandomForestClassifier(
        n_estimators=100, max_depth=10, class_weight="balanced", random_state=42, n_jobs=-1
    )
    rf_model.fit(df_train[FEATURES], df_train["Target"])
    print("Modelo treinado!")

    equipas = df_test["Equipa_Casa"].unique()
    tabela_real = {eq: 0 for eq in equipas}
    
    # Calcular pontos reais
    for _, row in jogos_passados.iterrows():
        res_real = le.classes_[row["Target"]]
        if res_real == "H":
            tabela_real[row["Equipa_Casa"]] += 3
        elif res_real == "A":
            tabela_real[row["Equipa_Visitante"]] += 3
        elif res_real == "D":
            tabela_real[row["Equipa_Casa"]] += 1
            tabela_real[row["Equipa_Visitante"]] += 1

    print(f"\\nTabela Real congelada (antes da jornada {jornada_alvo}):")
    top_5_reais = sorted(tabela_real.items(), key=lambda x: x[1], reverse=True)[:5]
    for eq, pts in top_5_reais:
        print(f" - {eq}: {pts} pontos")
        
    # 3. Simulação de Monte Carlo
    print(f"\\nA inciar Simulação de {num_simulacoes} iterações a partir da Jornada {jornada_alvo}...")
    
    campeoes_contagem = {eq: 0 for eq in equipas}
    
    # Obter probabilidades previamente para poupar tempo de execução
    X_futuro = jogos_futuros[FEATURES]
    probabilidades_futuro = rf_model.predict_proba(X_futuro)
    classes_modelo = le.classes_  # Array do formato ["A", "D", "H"] (tipicamente isso, depende do encode)
    
    for i in range(num_simulacoes):
        tabela_simulada = tabela_real.copy()
        
        # Simular todos os restantes jogos
        for idx_jogo, (_, row) in enumerate(jogos_futuros.iterrows()):
            probs_jogo = probabilidades_futuro[idx_jogo]
            
            # Tirar à sorte com base nas probabilidades dadas pelo predict_proba
            res_simulado = np.random.choice(classes_modelo, p=probs_jogo)
            
            # Adicionar os pontos da simulação
            if res_simulado == "H":
                tabela_simulada[row["Equipa_Casa"]] += 3
            elif res_simulado == "A":
                tabela_simulada[row["Equipa_Visitante"]] += 3
            elif res_simulado == "D":
                tabela_simulada[row["Equipa_Casa"]] += 1
                tabela_simulada[row["Equipa_Visitante"]] += 1
                
        # Detetar quem venceu nesta iteração
        classificacao_final = sorted(tabela_simulada.items(), key=lambda x: x[1], reverse=True)
        campeao = classificacao_final[0][0]
        
        # Em caso de empate pontual no 1º lugar, vamos adotar o critério de quem aparecer primeiro,
        # visto que idealmente o confronto direto seria complexo implementar para simulações rápidas.
        
        campeoes_contagem[campeao] += 1

    # 4. Análise e Apresentação de Resultados
    print("\\n" + "="*50)
    print(f" RESULTADO DAS 1000 SIMULAÇÕES MONTE CARLO")
    print(f" (Iniciado na Jornada {jornada_alvo})")
    print("="*50)
    
    for equipa in ["Sporting CP", "Benfica", "Porto"]:
        vitorias = campeoes_contagem.get(equipa, 0)
        percentagem = (vitorias / num_simulacoes) * 100
        print(f" {equipa:<15}: {vitorias:>4} vitórias | {percentagem:>5.1f}% de probabilidade")
        
    for equipa, vitorias in sorted(campeoes_contagem.items(), key=lambda item: item[1], reverse=True):
        if equipa not in ["Sporting CP", "Benfica", "Porto"] and vitorias > 0:
            percentagem = (vitorias / num_simulacoes) * 100
            print(f" {equipa:<15}: {vitorias:>4} vitórias | {percentagem:>5.1f}% de probabilidade")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulação Monte Carlo para o Campeão da Liga.")
    parser.add_argument("--jornada", type=int, default=28, help="Jornada alvo para arrancar a simulação (os jogos anteriores assumem os resultados reias).")
    parser.add_argument("--iters", type=int, default=1000, help="Número de iterações.")
    args = parser.parse_args()
    
    main(args.jornada, args.iters)
