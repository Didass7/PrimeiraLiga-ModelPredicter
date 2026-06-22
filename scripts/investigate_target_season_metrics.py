import sys
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
from sklearn.utils.class_weight import compute_sample_weight
from xgboost import XGBClassifier

# Adicionar root ao path para podermos importar o módulo da aplicação
import os
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from app.monte_carlo import load_and_prepare_data, FEATURES, apply_feature_decay

# Carregar dados usando a preparação do app
df = load_and_prepare_data()
df = df.dropna(subset=FEATURES).copy()

le = LabelEncoder()
df["Target"] = le.fit_transform(df["Resultado_Final"])
classes = list(le.classes_)

# Divisão por épocas (Treino em épocas passadas, Teste na época alvo 2025-2026)
epoca_alvo = "2025-2026"
df_train = df[df["Epoca"] != epoca_alvo].copy()
df_test = df[df["Epoca"] == epoca_alvo].copy()

# Aplicar Feature Decay
df_train_decayed = apply_feature_decay(df_train)
df_test_decayed = apply_feature_decay(df_test)

X_train = df_train_decayed[FEATURES]
y_train = df_train_decayed["Target"].values
X_test = df_test_decayed[FEATURES]
y_test = df_test_decayed["Target"].values

print(f"Shapes: Train {X_train.shape}, Test {X_test.shape}")
print(f"Classes Mapeadas: {classes}")

# 1. Random Forest
rf = RandomForestClassifier(
    n_estimators=100, max_depth=4, min_samples_leaf=8, min_samples_split=10,
    max_features=0.2, class_weight="balanced", random_state=42, n_jobs=-1
)
rf.fit(X_train, y_train)
y_pred_rf = rf.predict(X_test)
print("\n--- RANDOM FOREST ---")
print(classification_report(y_test, y_pred_rf, target_names=classes))

# 2. XGBoost
xgb = XGBClassifier(
    objective='multi:softprob', num_class=3, n_estimators=100, learning_rate=0.05,
    max_depth=4, random_state=42, eval_metric='mlogloss', n_jobs=-1
)
sample_weights = compute_sample_weight(class_weight='balanced', y=y_train)
xgb.fit(X_train, y_train, sample_weight=sample_weights)
y_pred_xgb = xgb.predict(X_test)
print("\n--- XGBOOST ---")
print(classification_report(y_test, y_pred_xgb, target_names=classes))

# 3. Logistic Regression
lr = LogisticRegression(solver='lbfgs', max_iter=1000, random_state=42, class_weight='balanced')
lr.fit(X_train, y_train)
y_pred_lr = lr.predict(X_test)
print("\n--- LOGISTIC REGRESSION ---")
print(classification_report(y_test, y_pred_lr, target_names=classes))

# 4. Decision Tree
dt = DecisionTreeClassifier(max_depth=4, class_weight='balanced', random_state=42)
dt.fit(X_train, y_train)
y_pred_dt = dt.predict(X_test)
print("\n--- DECISION TREE ---")
print(classification_report(y_test, y_pred_dt, target_names=classes))
