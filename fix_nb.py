import json

nb = {
 'cells': [
  {
   'cell_type': 'markdown',
   'metadata': {},
   'source': [
    '# \ud83d\udd04 Avaliação Jornada a Jornada (Temporal Rollout)\n',
    'Este notebook junta as tuas features avançadas (`Modelacao_RandomForest.py`) com o novo sistema de avaliação sequencial.'
   ]
  },
  {
   'cell_type': 'code',
   'execution_count': None,
   'metadata': {},
   'outputs': [],
   'source': [
    'import pandas as pd\n',
    'import numpy as np\n',
    'import matplotlib.pyplot as plt\n',
    'import seaborn as sns\n',
    'from sklearn.ensemble import RandomForestClassifier\n',
    'from sklearn.preprocessing import LabelEncoder\n',
    'from sklearn.metrics import accuracy_score, classification_report, confusion_matrix'
   ]
  },
  {
   'cell_type': 'markdown',
   'metadata': {},
   'source': [
    '## 1. Carregamento dos Dados Avançados\n',
    'Carregamos o dataset de features avançadas e preparamos a cronologia (Jornada) se esta não existir de forma explícita.'
   ]
  },
  {
   'cell_type': 'code',
   'execution_count': None,
   'metadata': {},
   'outputs': [],
   'source': [
    'try:\n',
    '    # Ajusta o caminho se necessário\n',
    '    df = pd.read_csv(r"..\\Datasets\\dataset_features_avancadas.csv", low_memory=False)\n',
    '    print("Dataset carregado com sucesso!")\n',
    'except FileNotFoundError:\n",
    '    try:\n',
    '        df = pd.read_csv(r"d:\\Diogo\\Ambiente de Trabalho\\PROJETO\\Datasets\\dataset_features_avancadas.csv", low_memory=False)\n',
    '        print("Dataset carregado pelo caminho absoluto com sucesso!")\n',
    '    except:\n',
    '        print("Erro: Ficheiro não encontrado.")\n',
    '\n',
    'if "Data" in df.columns:\n',
    '    df["Data"] = pd.to_datetime(df["Data"], dayfirst=True, errors="coerce")\n',
    '    df = df.dropna(subset=["Data"]).sort_values("Data").reset_index(drop=True)\n',
    '    \n',
    '    # Criar coluna Epoca se não existir\n',
    '    if "Epoca" not in df.columns:\n',
    '        def get_season(date):\n',
    '            return f"{date.year}-{date.year+1}" if date.month >= 7 else f"{date.year-1}-{date.year}"\n',
    '        df["Epoca"] = df["Data"].apply(get_season)\n',
    '    \n',
    '    # Criar Jornada se não existir\n',
    '    if "Jornada" not in df.columns:\n',
    '        def compute_jornadas(season_df):\n',
    '            season_df = season_df.copy()\n',
    '            team_games = {}\n',
    '            jornadas = []\n',
    '            for idx, row in season_df.iterrows():\n',
    '                home, away = row["Equipa_Casa"], row["Equipa_Visitante"]\n',
    '                hg, ag = team_games.get(home, 0), team_games.get(away, 0)\n',
    '                matchday = max(hg, ag) + 1\n',
    '                jornadas.append(matchday)\n',
    '                team_games[home] = hg + 1\n",
    '                team_games[away] = ag + 1\n",
    '            season_df["Jornada"] = jornadas\n',
    '            return season_df\n',
    '        df = df.groupby("Epoca", group_keys=False).apply(compute_jornadas).sort_values("Data").reset_index(drop=True)\n',
    '        print("Coluna Jornada gerada a partir das Datas.")'
   ]
  },
  {
   'cell_type': 'markdown',
   'metadata': {},
   'source': [
    '## 2. Definição de Features e Target (Retirado de Modelacao_RandomForest.py)'
   ]
  },
  {
   'cell_type': 'code',
   'execution_count': None,
   'metadata': {},
   'outputs': [],
   'source': [
    'features = [\n',
    '    "Home_hist_Pontos", "Home_hist_GolosMarcados", "Home_hist_GolosSofridos",\n',
    '    "Home_hist_DiferençaDeGolos", "Home_hist_Vitórias", "Home_hist_Derrotas", "Home_hist_Empates",\n',
    '    "Away_hist_Pontos", "Away_hist_GolosMarcados", "Away_hist_GolosSofridos",\n',
    '    "Away_hist_DiferençaDeGolos", "Away_hist_Vitórias", "Away_hist_Derrotas", "Away_hist_Empates",\n',
    '    \n',
    '    "Casa_Form_Pts5", "Casa_Form_GM5", "Casa_Form_GS5",\n',
    '    "Visitante_Form_Pts5", "Visitante_Form_GM5", "Visitante_Form_GS5",\n',
    '    "Casa_Form_Empates5", "Visitante_Form_Empates5",\n',
    '    \n",
    '    "Home_hist_GolosEsperados", "Home_hist_GolosEsperadosSofridos",\n',
    '    "Away_hist_GolosEsperados", "Away_hist_GolosEsperadosSofridos",\n',
    '    "Home_hist_PosseDeBola", "Away_hist_PosseDeBola",\n',
    '    "Home_hist_PassesProgressivos", "Away_hist_PassesProgressivos",\n",
    '    "Home_hist_JogosSemSofrerGolos", "Away_hist_JogosSemSofrerGolos",\n',
    '    \n',
    '    "Casa_Elo_PreJogo", "Visitante_Elo_PreJogo", "Diff_Elo",\n',
    '    "Casa_ExpectedGolos", "Visitante_ExpectedGolos", "Prob_Empate_Poisson",\n',
    '    "Casa_BTTS_Rate_5J", "Visitante_BTTS_Rate_5J",\n',
    '    "Casa_CleanSheet_Rate_5J", "Visitante_CleanSheet_Rate_5J",\n',
    '    "Casa_Rolling5_Remates", "Visitante_Rolling5_Remates",\n",
    '    "Casa_Rolling5_RematesAlvo", "Visitante_Rolling5_RematesAlvo",\n',
    '    "Casa_Rolling5_Cantos", "Visitante_Rolling5_Cantos"\n',
    ']\n',
    '\n',
    'df = df.dropna(subset=features)\n',
    '\n',
    'le = LabelEncoder()\n',
    'df["Resultado_Final_Encoded"] = le.fit_transform(df["Resultado_Final"])\n',
    'target = "Resultado_Final_Encoded"\n',
    'print(f"Classes Mapeadas: {list(zip(le.classes_, le.transform(le.classes_)))}\\n")\n',
    '\n',
    '# Vamos dividir exatamente aos 80% do tempo (mantendo a cronologia)\n',
    'split_idx = int(len(df) * 0.8)\n',
    'train_df = df.iloc[:split_idx].copy()\n',
    'test_df = df.iloc[split_idx:].copy()\n',
    '\n',
    'print(f"Treino: {len(train_df)} jogos | Teste: {len(test_df)} jogos")'
   ]
  },
  {
   'cell_type': 'markdown',
   'metadata': {},
   'source': [
    '## 3. Estrutura Avançada do Temporal Rollout'
   ]
  },
  {
   'cell_type': 'code',
   'execution_count': None,
   'metadata': {},
   'outputs': [],
   'source': [
    'rf_model = RandomForestClassifier(\n',
    '    n_estimators=100,\n',
    '    max_depth=10,\n',
    '    class_weight="balanced",\n',
    '    random_state=42,\n',
    '    n_jobs=-1\n',
    ')\n',
    '\n',
    'def executar_temporal_rollout(train_df, test_df, model, features, target):\n',
    '    print("A treinar base a partir do Histórico Antigo...")\n",
    '    model.fit(train_df[features], train_df[target])\n',
    '    \n',
    '    # Pegamos nas épocas e jornadas únicas ordenadas da secção de Teste\n',
    '    lista_rondas = test_df[["Epoca", "Jornada"]].drop_duplicates().values\n',
    '    \n',
    '    analise_campeao_por_jornada = {}\n',
    '    todas_as_previsoes = []\n',
    '    tabelas_por_epoca = {}\n',
    '    \n',
    '    for epoca, jornada in lista_rondas:\n',
    '        if epoca not in tabelas_por_epoca:\n",
    '            equipas_desta_epoca = test_df[test_df["Epoca"] == epoca]["Equipa_Casa"].unique()\n',
    '            tabelas_por_epoca[epoca] = {equipa: 0 for equipa in equipas_desta_epoca}\n',
    '            \n',
    '        tabela_classificativa = tabelas_por_epoca[epoca]\n',
    '        \n',
    '        jogos_desta_jornada = test_df[(test_df["Epoca"] == epoca) & (test_df["Jornada"] == jornada)]\n',
    '        jogos_futuros = test_df[(test_df["Epoca"] == epoca) & (test_df["Jornada"] > jornada)]\n',
    '        \n',
    '        if jogos_desta_jornada.empty:\n',
    '            continue\n",
    '            \n',
    '        # PREVISÃO DA JORNADA ATUAL\n',
    '        preds_jornada = model.predict(jogos_desta_jornada[features])\n',
    '        \n",
    '        for iter_idx, (idx, row) in enumerate(jogos_desta_jornada.iterrows()):\n',
    '            todas_as_previsoes.append({\n',
    '                "Epoca": epoca,\n',
    '                "Jornada": jornada,\n",
    '                "Data": row["Data"],\n',
    '                "Equipa_Casa": row["Equipa_Casa"],\n',
    '                "Equipa_Visitante": row["Equipa_Visitante"],\n',
    '                "Previsao": preds_jornada[iter_idx],\n',
    '                "Real": row[target]\n',
    '            })\n',
    '            \n',
    '        # SIMULAR QUEM É O CAMPEÃO (Prevendo a jornada atual e restos dos jogos daquela época!)\n',
    '        tabela_simulada = tabela_classificativa.copy()\n',
    '        \n',
    '        for iter_idx, (idx, row) in enumerate(jogos_desta_jornada.iterrows()):\n',
    '            prev = preds_jornada[iter_idx]\n',
    '            res_str = le.classes_[prev]\n',
    '            if res_str == "H":   tabela_simulada[row["Equipa_Casa"]] += 3\n",
    '            elif res_str == "D": \n',
    '                tabela_simulada[row["Equipa_Casa"]] += 1\n",
    '                tabela_simulada[row["Equipa_Visitante"]] += 1\n",
    '            elif res_str == "A": tabela_simulada[row["Equipa_Visitante"]] += 3\n",
    '                \n',
    '        if not jogos_futuros.empty:\n',
    '            preds_futuro = model.predict(jogos_futuros[features])\n',
    '            for iter_idx, (idx, row) in enumerate(jogos_futuros.iterrows()):\n",
    '                prev_fut = preds_futuro[iter_idx]\n',
    '                res_str = le.classes_[prev_fut]\n',
    '                if res_str == "H":   tabela_simulada[row["Equipa_Casa"]] += 3\n",
    '                elif res_str == "D": \n",
    '                    tabela_simulada[row["Equipa_Casa"]] += 1\n",
    '                    tabela_simulada[row["Equipa_Visitante"]] += 1\n",
    '                elif res_str == "A": tabela_simulada[row["Equipa_Visitante"]] += 3\n",
    '                    \n",
    '        try:\n",
    '            classificacao = sorted(tabela_simulada.items(), key=lambda x: x[1], reverse=True)\n",
    '            campeao_simulado, pontos_campeao = classificacao[0][0], classificacao[0][1]\n",
    '            analise_campeao_por_jornada[f"{epoca} | J{jornada:02d}"] = (campeao_simulado, pontos_campeao)\n',
    '        except:\n",
    '            pass\n",
    '            \n',
    '        # ATUALIZAR REALIDADE DO CAMPEONATO DA ÉPOCA\n',
    '        for idx, row in jogos_desta_jornada.iterrows():\n",
    '            res_real = le.classes_[row[target]]\n',
    '            if res_real == "H":   tabela_classificativa[row["Equipa_Casa"]] += 3\n",
    '            elif res_real == "D": \n",
    '                tabela_classificativa[row["Equipa_Casa"]] += 1\n",
    '                tabela_classificativa[row["Equipa_Visitante"]] += 1\n",
    '            elif res_real == "A": tabela_classificativa[row["Equipa_Visitante"]] += 3\n",
    '                \n",
    '        # RE-FIT COM OS NOVOS DADOS NA ÚLTIMA JORNADA\n",
    '        train_df = pd.concat([train_df, jogos_desta_jornada], ignore_index=True)\n",
    '        model.fit(train_df[features], train_df[target])\n",
    '        \n",
    '    return pd.DataFrame(todas_as_previsoes), analise_campeao_por_jornada'
   ]
  },
  {
   'cell_type': 'markdown',
   'metadata': {},
   'source': [
    '## 4. Resultados e Avaliação da Lógica Temporal'
   ]
  },
  {
   'cell_type': 'code',
   'execution_count': None,
   'metadata': {},
   'outputs': [],
   'source': [
    'resultados_df, historico_campeoes = executar_temporal_rollout(train_df, test_df, rf_model, features, target)\n",
    '\n',
    'resultados_df["Acertou"] = resultados_df["Previsao"] == resultados_df["Real"]\n",
    'acuracia = resultados_df["Acertou"].mean()\n",
    'print(f"\\n>> Accuracy Final (Temporal Rollout): {acuracia:.3f}")\n",
    '\n',
    'print("\\n--- Relatório Final de Classificação ---")\n",
    'print(classification_report(resultados_df["Real"], resultados_df["Previsao"], target_names=le.classes_))\n",
    '\n',
    'cm = confusion_matrix(resultados_df["Real"], resultados_df["Previsao"])\n",
    'plt.figure(figsize=(6, 4))\n",
    'sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=le.classes_, yticklabels=le.classes_)\n",
    'plt.title("Matriz de Confusão - Temporal Rollout")\n",
    'plt.ylabel("Real")\n",
    'plt.xlabel("Previsão")\n",
    'plt.show()\n",
    '\n',
    'print("\\nHistórico do Campeão Simulado (Final de cada Jornada):")\n",
    'for camp_key, (camp, pts) in list(historico_campeoes.items()):\n",
    '    print(f" - Pós-Jornada {camp_key}: {camp} com {pts} pts")'
   ]
  }
 ],
 'metadata': {
  'kernelspec': {
   'display_name': 'Python 3',
   'language': 'python',
   'name': 'python3'
  },
  'language_info': {
   'name': 'python',
   'version': '3'
  }
 },
 'nbformat': 4,
 'nbformat_minor': 4
}

with open(r'd:\Diogo\Ambiente de Trabalho\PROJETO\Notebooks\Modelacao_Temporal_Rollout.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print('Success')
