import sys
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, recall_score, f1_score
from sklearn.utils.class_weight import compute_sample_weight
from xgboost import XGBClassifier
import os

# Adicionar a pasta raiz do projeto ao sys.path para podermos importar o módulo da aplicação
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from app.monte_carlo import load_and_prepare_data, FEATURES, apply_feature_decay

# Carregar dados preparados
df = load_and_prepare_data()
df = df.dropna(subset=FEATURES).copy()

le = LabelEncoder()
df["Target"] = le.fit_transform(df["Resultado_Final"])
classes = list(le.classes_)

# Parâmetros da validação para o diagnóstico
epoca_alvo = "2025-2026"
jornada_alvo = 17

df_train = df[df["Epoca"] != epoca_alvo].copy()
df_test = df[df["Epoca"] == epoca_alvo].copy()

# Jogos passados da época alvo (Jornada < 17)
jogos_passados = df_test[df_test["Jornada"] < target_jornada] if 'target_jornada' in locals() else df_test[df_test["Jornada"] < 17]

# Aplicar Feature Decay
df_train_decayed = apply_feature_decay(df_train)
df_test_decayed = apply_feature_decay(jogos_passados)

X_train = df_train_decayed[FEATURES]
y_train = df_train_decayed["Target"].values
X_test = df_test_decayed[FEATURES]
y_test = df_test_decayed["Target"].values

print(f"Shapes: Train {X_train.shape}, Test {X_test.shape}")
print(f"Classes: {classes}")

# Função para printar métricas compatíveis com a tabela do utilizador
def print_metrics(model_name, y_true, y_pred):
    acc = accuracy_score(y_true, y_pred)
    # Recall Geral (weighted average of recall)
    rec_geral = recall_score(y_true, y_pred, average='weighted')
    # Recall de Empates ('D')
    d_idx = classes.index('D')
    rec_empates = recall_score(y_true, y_pred, labels=[d_idx], average='macro')
    # F1-Score Macro
    f1_macro = f1_score(y_true, y_pred, average='macro')
    
    print(f"\n--- {model_name} ---")
    print(f"Exatidão Global: {acc*100:.1f}%")
    print(f"Recall Geral: {rec_geral*100:.1f}%")
    print(f"Recall Empates: {rec_empates*100:.2f}%")
    print(f"F1-Score (Macro): {f1_macro:.2f}")

# 1. Random Forest
rf = RandomForestClassifier(
    n_estimators=100, max_depth=4, min_samples_leaf=8, min_samples_split=10,
    max_features=0.2, class_weight="balanced", random_state=42, n_jobs=-1
)
rf.fit(X_train, y_train)
y_pred_rf = rf.predict(X_test)
print_metrics("RANDOM FOREST (Otimizado)", y_test, y_pred_rf)

# 2. XGBoost
xgb = XGBClassifier(
    objective='multi:softprob', num_class=3, n_estimators=100, learning_rate=0.05,
    max_depth=4, random_state=42, eval_metric='mlogloss', n_jobs=-1
)
sample_weights = compute_sample_weight(class_weight='balanced', y=y_train)
xgb.fit(X_train, y_train, sample_weight=sample_weights)
y_pred_xgb = xgb.predict(X_test)
print_metrics("XGBOOST", y_test, y_pred_xgb)

# 3. Logistic Regression
lr = LogisticRegression(solver='lbfgs', max_iter=1000, random_state=42, class_weight='balanced')
lr.fit(X_train, y_train)
y_pred_lr = lr.predict(X_test)
print_metrics("REGRESSÃO LOGÍSTICA (Baseline)", y_test, y_pred_lr)

# 4. Decision Tree
dt = DecisionTreeClassifier(max_depth=4, class_weight='balanced', random_state=42)
dt.fit(X_train, y_train)
y_pred_dt = dt.predict(X_test)
print_metrics("ÁRVORE DE DECISÃO", y_test, y_pred_dt)
