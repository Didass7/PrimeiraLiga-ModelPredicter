import nbformat as nbf

nb = nbf.v4.new_notebook()

nb.cells = [
    nbf.v4.new_markdown_cell("# Previsão Jornada a Jornada - Época 23/24\n\nNeste notebook vamos simular a previsão passo a passo (ou jogo a jogo) para a época de 23/24, garantindo que o modelo Random Forest com `class_weight='balanced'` só utiliza a informação disponível até ao momento do jogo."),
    
    nbf.v4.new_code_cell("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder
from IPython.display import display"""),

    nbf.v4.new_markdown_cell("## 1. Carregar Dados e Preparar Features"),
    nbf.v4.new_code_cell("""# Carregar Dados
df = pd.read_csv(r"Datasets\dataset_features_avancadas.csv", low_memory=False)

# Garantir que a coluna Data é datetime para podermos ordenar
df['Data'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce')
df = df.sort_values(by='Data').reset_index(drop=True)

print("Dataset carregado. Total de jogos:", len(df))"""),

    nbf.v4.new_code_cell("""# Definir as features (Avançadas)
features = [
    'Home_hist_Pontos', 'Home_hist_GolosMarcados', 'Home_hist_GolosSofridos',
    'Home_hist_DiferençaDeGolos', 'Home_hist_Vitórias', 'Home_hist_Derrotas', 'Home_hist_Empates',
    'Away_hist_Pontos', 'Away_hist_GolosMarcados', 'Away_hist_GolosSofridos',
    'Away_hist_DiferençaDeGolos', 'Away_hist_Vitórias', 'Away_hist_Derrotas', 'Away_hist_Empates',
    
    'Casa_Form_Pts5', 'Casa_Form_GM5', 'Casa_Form_GS5',
    'Visitante_Form_Pts5', 'Visitante_Form_GM5', 'Visitante_Form_GS5',
    'Casa_Form_Empates5', 'Visitante_Form_Empates5',
    
    'Home_hist_GolosEsperados', 'Home_hist_GolosEsperadosSofridos',
    'Away_hist_GolosEsperados', 'Away_hist_GolosEsperadosSofridos',
    'Home_hist_PosseDeBola', 'Away_hist_PosseDeBola',
    'Home_hist_PassesProgressivos', 'Away_hist_PassesProgressivos',
    'Home_hist_JogosSemSofrerGolos', 'Away_hist_JogosSemSofrerGolos',
    
    'Casa_Elo_PreJogo', 'Visitante_Elo_PreJogo', 'Diff_Elo',
    'Casa_ExpectedGolos', 'Visitante_ExpectedGolos', 'Prob_Empate_Poisson',
    
    'Casa_BTTS_Rate_5J', 'Visitante_BTTS_Rate_5J',
    'Casa_CleanSheet_Rate_5J', 'Visitante_CleanSheet_Rate_5J',
    'Casa_Rolling5_Remates', 'Visitante_Rolling5_Remates',
    'Casa_Rolling5_RematesAlvo', 'Visitante_Rolling5_RematesAlvo',
    'Casa_Rolling5_Cantos', 'Visitante_Rolling5_Cantos'
]

# Remover linhas que não têm todas as features preenchidas (necessário para o RF)
df_clean = df.dropna(subset=features + ['Resultado_Final', 'Season', 'Data', 'Equipa_Casa', 'Equipa_Visitante']).copy()

# Encoding do Target (0: Casa, 1: Empate, 2: Fora - dependendo da ordem)
le = LabelEncoder()
df_clean['Target'] = le.fit_transform(df_clean['Resultado_Final'])

# Mapeamento para visualização
classes_map = dict(zip(le.transform(le.classes_), le.classes_))
print("Classes mapeadas:", classes_map)
"""),

    nbf.v4.new_markdown_cell("## 2. Treinar o Modelo até 2022/2023\n\nVamos usar todos os jogos das épocas anteriores à 2023/2024 para treinar o nosso modelo."),
    nbf.v4.new_code_cell("""# Filtrar histórico (tudo o que for antes da época 23/24)
# O dataset tem a coluna 'Season' que regista a época, ou podemos usar o ano da 'Data'
# Vamos usar a coluna Season, assumindo que 23/24 está escrito de alguma forma.
# Para evitar problemas com a formatação da época, também podemos simplesmente dividir pela data:
# Época 23/24 começou em Agosto de 2023.
train_df = df_clean[df_clean['Data'] < '2023-08-01']
test_df = df_clean[df_clean['Data'] >= '2023-08-01'] # Aqui estão os jogos da época 23/24 em diante

X_train = train_df[features]
y_train = train_df['Target']

print(f"Jogos para treino: {len(train_df)}")
print(f"Jogos para teste (Época 23/24+): {len(test_df)}")

# Configurar e Treinar Random Forest (Balanced)
rf_model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    class_weight='balanced',
    random_state=42,
    n_jobs=-1
)

print("A treinar o modelo...")
rf_model.fit(X_train, y_train)
print("Modelo Treinado!")
"""),

    nbf.v4.new_markdown_cell("## 3. Previsão Jogo a Jogo (Simulação de Jornadas)\n\nAgora vamos iterar sobre os jogos de 23/24, apresentando a previsão para cada um deles. As probabilidades ajudarão a ver a confiança do modelo."),
    nbf.v4.new_code_cell("""# Vamos criar um DataFrame para guardar os resultados
resultados = []

# Iterar sobre os jogos da Época 23/24 (que já estão ordenados por data)
for index, row in test_df.iterrows():
    # Extrair as features deste jogo específico (1 linha)
    jogo_features = row[features].values.reshape(1, -1)
    
    # Fazer a previsão e extrair as probabilidades
    pred_target = rf_model.predict(jogo_features)[0]
    probabilidades = rf_model.predict_proba(jogo_features)[0]
    
    # Descodificar o target e previsão para o texto (A, D, H)
    resultado_real = classes_map[row['Target']]
    previsao = classes_map[pred_target]
    
    # Estruturar as probabilidades num dicionário para fácil leitura
    probs_dict = {
        f"Prob {classes_map[0]}": round(probabilidades[0], 2),
        f"Prob {classes_map[1]}": round(probabilidades[1], 2),
        f"Prob {classes_map[2]}": round(probabilidades[2], 2)
    }
    
    # Avaliar se acertou
    acertou = (resultado_real == previsao)
    
    # Guardar no array de resultados
    resultados.append({
        'Data': row['Data'].strftime('%Y-%m-%d'),
        'Equipa Casa': row['Equipa_Casa'],
        'Equipa Fora': row['Equipa_Visitante'],
        'Real': resultado_real,
        'Previsão': previsao,
        'Acertou': 'Sim' if acertou else 'Não',
        **probs_dict
    })

# Converter para DataFrame para facilitar a visualização e análise
resultados_df = pd.DataFrame(resultados)

# Mostrar os primeiros 18 jogos (equivalente a 2 jornadas)
display(resultados_df.head(18))
"""),

    nbf.v4.new_markdown_cell("## 4. Análise de Performance Global nesta fase"),
    nbf.v4.new_code_cell("""# Calcular a Accuracy e o Recall dos Empates ('D')
acc = accuracy_score(test_df['Target'], rf_model.predict(test_df[features]))

print(f"Accuracy Geral na época 23/24: {acc:.3f}")

# Contagem de acertos por classe
acertos_por_classe = resultados_df[resultados_df['Acertou'] == 'Sim'].groupby('Real').size()
total_por_classe = resultados_df.groupby('Real').size()

recall_por_classe = (acertos_por_classe / total_por_classe).fillna(0)
print("\\nRecall por classe:")
print(recall_por_classe.round(3))

# Ver especificamente o desempenho nos jogos onde a previsão foi "Empate" (D)
previsoes_empate = resultados_df[resultados_df['Previsão'] == 'D']
if not previsoes_empate.empty:
    acerto_empates_previstos = previsoes_empate[previsoes_empate['Acertou'] == 'Sim'].shape[0] / previsoes_empate.shape[0]
    print(f"\\nDas vezes que o modelo apostou num Empate, acertou: {acerto_empates_previstos:.1%}")
else:
    print("\\nO modelo não previu nenhum Empate.")
""")
]

with open(r'Notebooks\Previsao_Jornada_RandomForest.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print("Notebook 'Previsao_Jornada_RandomForest.ipynb' criado com sucesso!")
