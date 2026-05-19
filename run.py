"""
Liga Predictor — Script de Arranque

Uso:
    python run.py

O servidor fica disponivel em: http://localhost:8000
"""

import uvicorn

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  Liga Predictor - Servidor a iniciar...")
    print("  http://localhost:8000")
    print("=" * 50 + "\n")

    uvicorn.run(
        "app.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
