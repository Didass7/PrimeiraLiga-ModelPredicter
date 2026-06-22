# ⚽ Liga Predictor — Previsão da Primeira Liga com Machine Learning

Este repositório contém o projeto de fim de curso para a **Licenciatura em Engenharia Informática**, focado na aplicação de técnicas avançadas de *Data Science*, *Machine Learning* e Simulação Estocástica de Monte Carlo para prever os desfechos dos jogos e projetar a tabela final da **Primeira Liga Portuguesa** de futebol.

O projeto inclui um pipeline de dados automatizado (ETL), modelagem estatística comparativa de múltiplos algoritmos de classificação e um servidor web interativo para visualizar previsões de jornadas e probabilidades de campeão em tempo real.

---

## 🚀 Funcionalidades Principais

*   **Pipeline de Dados Automatizado (ETL):** Integração automática com dados do *football-data.co.uk* e *FBRef* via GitHub Actions (correndo semanalmente) para manter os dados atualizados com os resultados de jogos reais e recalcular 16 *features* avançadas de forma automática.
*   **Modelos Preditivos de ML:** Implementação comparativa dos algoritmos **XGBoost**, **Random Forest**, **Regressão Logística** e **Árvore de Decisão** treinados com mais de 20 anos de dados históricos.
*   **Motor de Simulação de Monte Carlo:** Algoritmo estocástico que simula milhares de vezes os jogos restantes do campeonato para estimar probabilidades de título, qualificação europeia e descida de divisão de cada equipa.
*   **Interface Web Premium:** Painel interativo moderno com estética *dark mode/glassmorphism* construído com Vanilla CSS/JS para exploração dos dados e simulações, alimentado por um *backend* robusto em **FastAPI**.

---

## 📂 Estrutura do Repositório

O repositório está organizado de forma clara e modular:

```text
├── .github/workflows/      # Configurações do CI/CD (Pipeline agendado no Github Actions)
├── app/                    # Código-fonte da Aplicação Web e Backend
│   ├── api.py              # API FastAPI (Serviços e rotas da web app)
│   ├── monte_carlo.py      # Motor e lógica de simulação de Monte Carlo
│   └── static/             # Frontend da Web App (HTML, CSS e JavaScript)
├── Datasets/               # Armazenamento de dados e tabelas csv
│   ├── archive/            # Cópias históricas e datasets arquivados
│   ├── results/            # Resultados de simulações e métricas experimentais
│   └── ...                 # Ficheiros principais de treino (dataset_features_avancadas.csv)
├── docs/                   # Documentação auxiliar do projeto
│   ├── images/             # Imagens, esquemas e gráficos de performance do modelo
│   ├── diario.md           # Diário de desenvolvimento detalhado
│   └── dicionario_dados.md # Descrição detalhada de todas as colunas do dataset
├── Notebooks/              # Notebooks Jupyter para EDA, Modelagem e Experiências
├── pipeline/               # Pipeline de Dados (ETL)
│   ├── extract.py          # Script de recolha e extração
│   ├── transform.py        # Limpeza, merge e cálculo de features móveis
│   ├── load.py             # Gravação e consistência temporal na base de dados
│   ├── features_avancadas.py# Cálculo das 16 métricas avançadas (Elo, Poisson, Form)
│   └── run_all.py          # Script principal de execução do pipeline ETL
├── Relatório/              # Documentos académicos, enunciados e relatórios do projeto
├── run.py                  # Script de entrada para arranque do servidor local
└── requirements.txt        # Dependências de software do projeto
```

---

## 🛠️ Configuração e Instalação Local

Siga os passos abaixo para configurar e correr o projeto na sua máquina:

### 1. Pré-requisitos
*   Python 3.10 ou superior instalado.
*   (Opcional) Ambiente virtual recomendado.

### 2. Instalação das Dependências
Clone o repositório, navegue para o diretório raiz e instale os pacotes requeridos:
```bash
# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente virtual (Windows)
.venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

### 3. Executar o Servidor da Aplicação Web
Corra o script `run.py` para iniciar o servidor web FastAPI:
```bash
python run.py
```
O servidor ficará disponível localmente em: **[http://localhost:8000](http://localhost:8000)**. Abra o link no seu navegador para interagir com o painel preditivo.

---

## 📈 Pipeline de Dados (ETL)

O pipeline recolhe automaticamente dados de novos jogos concluídos e atualiza a base de dados. Caso deseje executar manualmente e de forma imediata o pipeline:
```bash
python pipeline/run_all.py
```

---

## 🔬 Scripts de Análise e Diagnóstico

Na pasta `scripts/` encontram-se programas úteis para validar o backend e avaliar o desempenho comparativo dos modelos de Machine Learning:

*   **Testar Simulação do Backend:**
    ```bash
    python scripts/check_backend_simulation.py
    ```
*   **Investigar Desempenho dos Modelos (Métricas Globais):**
    ```bash
    python scripts/investigate_all_models.py
    ```
*   **Avaliação na Época Alvo (Jornada 17):**
    ```bash
    python scripts/investigate_jornada17_metrics.py
    ```

---

## 📐 Detalhes Técnicos e Metodologia

1.  **Métricas Avançadas:**
    *   *Rating Elo:* Um sistema dinâmico que atualiza a força relativa de cada equipa com base na dificuldade do adversário.
    *   *Distribuição de Poisson:* Modelação de probabilidades de golos marcados e sofridos para prever probabilidades exatas de cada jogo (btss, clean-sheets, número de golos).
2.  **Mitigação de Data Leakage:**
    *   Os cálculos de forma móvel (*rolling features*) utilizam exclusivamente dados históricos dos jogos *anteriores* ao jogo alvo (`shift(1)`), assegurando que o modelo não acede a informações futuras no momento do treino ou previsão.
    *   Nas primeiras jornadas da época, é aplicado um fator de decaimento temporal para misturar progressivamente o peso do desempenho histórico da época passada com o da nova época.