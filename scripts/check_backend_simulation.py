import os
import sys

# Adicionar a pasta raiz do projeto ao sys.path para podermos importar o módulo da aplicação
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from app.monte_carlo import run_simulation

# Testar para cada modelo na época 2025-2026, jornada 17
modelos = ["Random Forest", "XGBoost", "Logistic Regression", "Decision Tree"]

for mod in modelos:
    print(f"\nA executar simulação para o modelo: {mod}...")
    res = run_simulation(
        epoca_alvo="2025-2026",
        jornada_alvo=17,
        num_simulacoes=10,  # poucas iterações para ser rápido
        modelo_alvo=mod
    )
    if "metricas_previsao" in res:
        mp = res["metricas_previsao"]
        if mp.get("disponivel"):
            print(f"Métricas do Backend:")
            print(f"  Accuracy: {mp['accuracy']}%")
            print(f"  Recall Casa (H): {mp['recall']['H']}%")
            print(f"  Recall Empate (D): {mp['recall']['D']}%")
            print(f"  Recall Visitante (A): {mp['recall']['A']}%")
        else:
            print("  Métricas não disponíveis no resultado.")
    else:
        print(f"  Erro ou formato inesperado: {res}")
