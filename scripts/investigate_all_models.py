import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
from sklearn.utils.class_weight import compute_sample_weight
from xgboost import XGBClassifier

def fix_mojibake(text):
    if not isinstance(text, str):
        return text
    try:
        return text.encode('latin-1').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text

# Carregar dados
try:
    import os
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dataset_path = os.path.join(ROOT_DIR, "Datasets", "dataset_features_avancadas.csv")
    df = pd.read_csv(dataset_path, low_memory=False, encoding='latin1')
    df.columns = [fix_mojibake(col) for col in df.columns]
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].apply(fix_mojibake)
    print("Dataset carregado.")
except Exception as e:
    print(f"Erro ao carregar dataset: {e}")
    exit(1)

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

df = df.dropna(subset=features)
X = df[features]
y = df['Resultado_Final']

le = LabelEncoder()
y = le.fit_transform(y)
classes = list(le.classes_)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

print(f"Dataset split: Train {X_train.shape}, Test {X_test.shape}")
print(f"Classes: {classes}")

# 1. Random Forest
rf = RandomForestClassifier(
    n_estimators=100, max_depth=4, min_samples_leaf=8, min_samples_split=10,
    max_features=0.2, class_weight='balanced', random_state=42, n_jobs=-1
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
