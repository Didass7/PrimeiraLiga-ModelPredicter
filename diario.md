# DiÃ¡rio de Desenvolvimento â€“ Projeto Liga Portuguesa ML

## 2025-09-24

- Pesquisei sites com datasets de interesse para o projeto; encontrei o FBref ([fbref.com](https://fbref.com/en/)) como o mais adequado e robusto.
- Analisei que o FBref tem todo o tipo de informaÃ§Ãµes das ultimas 25 Ã©pocas da Liga Portuguesa com 12 tabelas por Ã©poca
- Pesquisei formas de dar scrapping Ã s tabelas que existem no website
- Recolhi a estrutura das tabelas do FBref e analisei quais colunas seriam mais relevantes para o projeto
- Comecei a planear o dataset bruto (todas as tabelas juntas)
- Cheguei Ã  conclusÃ£o que o site que quero usar tem proteÃ§Ã£o contra scrapping por isso terei que retirar a informaÃ§Ã£o de forma manual

## 2025-09-25

- TraduÃ§Ã£o do nome das colunas no plano do Dataset Final para generalizar todas as colunas de todas as tabelas para depois unir tudo.
- ExtraÃ§Ã£o de todas as tabelas da Ã©poca 2024-2025
- CÃ³digo base para extrair as tabelas de cada Ã©poca, sÃ³ Ã© preciso trocar o link para cada ano
- Criado um Dataset Completo com todas as colunas de todas as tabelas da Ã©poca 2024-2025
- Problemas com colunas repetidas

## 2025-09-28

- Problema com colunas repetidas resolvido (havia colunas com nomes identicos ex: Assistencias e AssistÃªncias)
- Criei pastas para as Ãºltimas 20 Ã©pocas, penso que seja o suficiente para realizar a previsÃ£o

## 2025-09-30

- Notei que quanto menos recente a epoca for menos informaÃ§Ã£o o website tem.
- Comecei a tirar os dados da Ã©poca 2023-24
- Fartei-me de fazer tudo manualmente e decidi voltar a pesquisar por formas de fazer isto automÃ¡ticamente
- Descubri uma biblioteca chamada Selenium que dÃ¡ para simular um navegador real e contornar as proteÃ§oes do site
- Criei um script bÃ¡sico para tentar automatizar a navegaÃ§Ã£o para a pÃ¡gina de cada Ã©poca e extrair as tabelas
- Alguns problemas que tive para Ã©pocas mais antigas:
  * Faltavam colunas de estatÃ­stica como xG
  * Epocas com menos tabelas que as mais recentes
  * Erros com o merge por causa de dados inconsistentes na coluna 'Equipa'

## 2025-10-01

- Melhorei o script para prevenir erros para extrair apenas os dados existentes em cada Ã©poca
- Adicionei lÃ³gica para saltar tabelas em falta sem interromper a extraÃ§Ã£o
- Acabei a fase de recolha de dados com a geraÃ§Ã£o do ficheiro data_completo.csv com as ultimas 20 Ã©pocas
- Comecei a limpar dados do dataset (colunas duplicadas)
- Terminei a limpeza do dataset e renomei clubes com nomes iguais como 'Gil Vicente' e 'Gil Vicente FC'
- Acabei agora de recolher todos os dados que preciso para realizar o projeto

## 2025-10-11

- Comecei a fazer o relatorio
- Escrevi a IntroduÃ§Ã£o
- Comecei a pesquisar artigos e trabalhos identicos para fazer o estado da arte
- A principal fonte que encontrei foi o football-data.co.uk, tem os dados da Liga em CSV com estatÃ­sticas de jogo e adds de apostas
- A segunda principal que encontrei foi o Kaggle, nÃ£o me pareceu ser uma fonte muito viavel porcausa da qualidade e manutenÃ§Ã£o. Talvez seja Ãºtil mais para a frente para validaÃ§Ã£o
- Pesquisei sites como OpenFootball e football-data.org. O formato de dados no OpenFootball nÃ£o Ã© por tabelas e o football-data.org funciona com um API com um nÃ­vel gratuito limitado

## 2025-10-13

- Cheguei Ã  conclusÃ£o que o football-data.co.uk seria provavelmente a melhor fonte de dados para comeÃ§ar
- O FBRef Ã© uma boa fonte e tem dados que o football-data.co.uk nÃ£o tem
- Se juntasse os dados dos dois poderia criar um conjunto de dados mais robusto

## 2025-10-15

- Hoje pesquisei por sites que tentam resolver o mesmo problema que eu
- Vi o site "The application of machine learning techniques for predicting football match outcomes: a review" deu-me uma visÃ£o dos algoritmos mais comuns (Poisson, Redes Neuronais) e falou sobre a dificuldade em prever empates
- TambÃ©m vi o artigo sobre a Primeira Liga no Medium (Paulo Matos). Foi Ãºtil por ser algo focado na mesma liga que eu. Usou o FBRef e aplicou a Random Forest e XGBoost, falou tambÃ©m sobre a dificuldade de prever empates. Conseguiu atinger uma percentagem de certidÃ£o de 53% - 56%

## 2025-10-16

- Li outro artigo sobre Gradient Boosting (Lewandowsky & Chlebus, 2021). ReforÃ§ou a ideia que modelos de gradient boosting como XGBoost e CatBoost sÃ£o o estado da arte para este tipo de problemas superando outras abordagens
- Cheguei Ã  conclusÃ£o que os modelos de gradient boosting (XGBoost) sÃ£o a minha melhor opÃ§Ã£o

## 2025-10-18

- Li uma Tese chamada "Football Match Prediction using Deep Learning" (Shah, 2017). Apresentou o uso de redes Neuronais Recorrentes (LSTMs) para capturar a natureza sequencial do desempenho das equipas sÃ³ que usava dados que eram proprietÃ¡rios e melhores dos que temos acesso
- Vi uma ResivÃ£o de Bunker et al. (2024). Esta revisÃ£o mais recente concluiu que CNNs e LSTMs ainda nÃ£o conseguiram superar consistentemente o desempenho dos modelos de gradient boost como XGBoost
- ConclusÃ£o do dia: Deep Learning nÃ£o Ã© tÃ£o eficiente como Gradient Boosting

## 2025-10-19

- Pesquisei aplicaÃ§Ãµes com previsÃ£o desportiva
- Comecei pela NerdyTips que Ã© uma aplicaÃ§Ã£o que oferece alguma transparÃªncia sobre a sua tecnologia. Menciona um motor de IA baseado em Java ("NT Apex")
- A app Soccer Predictions Football AI e Sports AI sÃ£o exemplos de advanced machine learning e nÃ£o fornecem detalhes
- Vi tambÃ©m a app BettingPros E Action Network que sÃ£o plataformas que tÃªm previsÃµes com anÃ¡lise de especialistas
- Conclui que as apps comerciais tem muito pouca transparencia tÃ©cnica e isso torna-as uma fonte pouco fiavel para me guiar

## 2025-10-20

- Hoje pesquisei projetos que tentaram fazer o mesmo que eu no github
- O primeiro que chamou mais Ã  atenÃ§Ã£o foi o dagbolade/all_leagues-_prediction. Pareceu ser o mais completo, usa gradient boosting e usa um sistema de rating Elo
- O segundo foi o pawelp0499/football-prediction-model. Usa uma abordagem mais simples com RegressÃ£o LogÃ­stica Multinomial em R.
- Pelo que vi posso concluir que o padrÃ£o testado e comprovado foi o uso de Python, usando Pandas Scikit-learn/XGBoost para modelagem e Flask para uma possÃ­vel API

## 2025-10-20

- Apos alguns dias a pesquisar fiz um mini resumo com o que conclui:
  * Dados: combinar football-data.co.uk com os dados do FBRef
  * Algoritmos: o modelo principal deve ser XGBoost e posso usar um modelo de RegressÃ£o Logistica para comparar
  * Ideias: Criar um sistema de rating Elo para medir a forma das equipas
  * AvaliaÃ§Ã£o: Devo treinar em Ã©pocas passadas e testar nas mais recente para evitar data leakage. Devo usar F1-score para avaliar a previsÃ£o de empates e log-loss
- Posso comeÃ§ar a escrever o estado da arte no relatÃ³rio

## 2025-11-01

- Comecei a escrever o estado da arte no relatÃ³rio
- Pesquisei por alternativas para o docs para armazenar fontes dos artigos cientificos que andei a pesquisar
- Encontrei o Zotero e comecei a configurar e a aprender a usar

## 2025-11-03

- Escrevi mais um bocado do capitulo do estado da arte no relatorio
- Fui pesquisando de fundo sobre os datasets do football-data.co.uk e comecei a baixar os arquivos por Ã©poca

## 2025-11-06

- Pesquisei sobre a possibilidade de juntar os dois datasets (FBRef e football-data.co.uk) num Ãºnico data set
- Cheguei Ã  conclusÃ£o que Ã© possÃ­vel sÃ³ que Ã© preciso ter cuidado com a data leakeage, por exemplo:
  * PrevisÃ£o de um jogo Benfica-Sporting na 5Âª jornada de 2023/2024. Se usarmos estatisticas finais dessa mesma Ã©poca (do FBRef), iremos estar a dar acesso ao modelo a informaÃ§Ãµes que ainda nÃ£o aconteceram.
- Teria que fazer alguma mudanÃ§a no dataset do FBRef para nÃ£o haver este problema de data leakage
- Escrevi mais um bocado do relatorio

## 2025-11-12

- Cheguei Ã  conclusÃ£o que os dados do football_data.co.uk serÃ£o a espinha dorsal do modelo com as informaÃ§Ãµes jogo a jogo.
- Os dados do FBRef devem ser usados para contexto historico, ou seja, para prever um jogo da Ã©poca 2023-2024, alimentamos o modelo com estatÃ­sticas agregadas da Ã©poca 2022-2023
- Comecei por juntar todos os ficheiros csv do football_data.co.uk que estavam separados por Ã©pocas
- Depois deparei-me com um problema entre os dois datasets. Os nomes das equipas estavam diferentes, ex: Num "Sporting CP" e no outro "Sporting" 

## 2025-11-16

- Decidi avanÃ§ar com a junÃ§Ã£o dos dois datasets. O plano Ã© usar o football-data.co.uk como base e adicionar as colunas do FBRef.
- Tive a analisar os ficheiros e o primeiro passo vai ser uniformizar os nomes das equipas.
- Vou criar um script para carregar tudo e identificar estas diferenÃ§as para criar um dicionÃ¡rio de mapeamento.
- Identifiquei as diferenÃ§as nos nomes das equipas (ex: "Sp Braga" vs "Braga", "Guimaraes" vs "VitÃ³ria") e criei o dicionÃ¡rio de mapeamento completo.

## 2025-11-20

- Implementei a lÃ³gica de fusÃ£o (merge) dos datasets: para cada jogo, juntei as estatÃ­sticas do FBRef da Ã©poca anterior para garantir que o modelo usa apenas dados histÃ³ricos (evitando data leakage).
- Corrigi alguns erros de execuÃ§Ã£o (datas invÃ¡lidas e avisos de performance) e gerei com sucesso o ficheiro `dataset_final_merged.csv`.
- O objetivo Ã© deixar tudo pronto para depois aplicar o XGBoost.

## 2025-11-23

- Analisei o dataset criado e detetei 3 problemas crÃ­ticos:
    1.  **RecÃ©m-Promovidos:** Equipas que sobem de divisÃ£o nÃ£o tÃªm histÃ³rico na Ã©poca anterior, gerando `NaNs`.
    2.  **Lixo:** Colunas `Unnamed` que nÃ£o servem para nada.
    3.  **Datas e Odds:** Datas em texto e falta de dados em Ã©pocas antigas.
- Decidi a soluÃ§Ã£o para os recÃ©m-promovidos: vou preencher os dados em falta com a **mÃ©dia das 3 piores equipas da Ã©poca anterior**. Ã‰ uma aproximaÃ§Ã£o justa (quem sobe costuma lutar para nÃ£o descer).
- Atualizei o script `preparacao_dados.ipynb` para incluir esta lÃ³gica de imputaÃ§Ã£o e limpar o resto.


## 2025-11-25

- Renomeei todas as colunas para PortuguÃªs (sem abreviaturas) para facilitar a leitura.
- Criei o `DICIONARIO_DADOS.md` para documentar o significado de cada coluna.

## 2025-11-30
- Criei o notebook `Modelacao_XGBoost.ipynb` para comeÃ§ar a parte mais interessante: treinar o modelo! Vou comeÃ§ar por usar os dados histÃ³ricos e as odds para ver se consigo bater as casas de apostas.

## 2025-12-10
  * **Target:** 0 (Casa), 1 (Empate), 2 (Visitante).
  * **Features:** Estou a usar as Odds (que jÃ¡ trazem muita informaÃ§Ã£o do mercado) e as mÃ©dias da Ã©poca anterior do FBRef (para evitar data leakage, i.e., nÃ£o usar dados do futuro para prever o passado).
  * **Split:** Treino atÃ© 2023, Teste na Ã©poca 2023/24. Ã‰ a forma mais honesta de validar porque simula a previsÃ£o real.
  * **Algoritmo:** XGBoost com `multi:softprob`. Basicamente ele cria centenas de Ã¡rvores de decisÃ£o onde cada uma tenta corrigir os erros da anterior.

## 2025-12-15
- Corri o modelo e tive 55% de accuracy no conjunto de teste. NÃ£o Ã© mau para comeÃ§ar.
- O modelo falha muito a prever os empates, o que jÃ¡ estava Ã  espera. Vou ter que investigar como melhorar isto.

## 2025-12-18
- Criei baselines para comparar resultados:
  * **RegressÃ£o LogÃ­stica:** 57% Accuracy (superior ao XGBoost inicial!). Isto sugere que o problema pode ser parcialmente linear ou que o XGBoost precisa de melhor afinaÃ§Ã£o.
  * **Ãrvore de DecisÃ£o:** 53% Accuracy.
  * ConclusÃ£o: O XGBoost (55%) nÃ£o estÃ¡ a "aprender" muito mais do que uma simples regressÃ£o linear das odds. Tenho de trabalhar nas features.

## 2025-12-23
**[DIAGNÃ“STICO XGBoost]**
  * **Overfitting Massivo:** Accuracy Treino 95% vs Teste 52%. O modelo decorou os dados de treino completamente.
  * **Feature Importance:** O modelo estÃ¡ dependente quase exclusivamente de `Home_hist_Pontos` e `Away_hist_Pontos`.
  * **PrÃ³ximos Passos:** Preciso de RegularizaÃ§Ã£o (reduzir `max_depth`, aumentar `min_child_weight`) e talvez reduzir o nÃºmero de features para evitar ruÃ­do.

## 2025-12-26
- **[OTIMIZAÃ‡ÃƒO XGBoost]**
  * Executei `GridSearchCV` para encontrar os melhores hiperparÃ¢metros.
  * **Melhores ParÃ¢metros:** `max_depth=3` (reduzido de 6), `learning_rate=0.01` (mais lento), `n_estimators=200`.
  * **Resultados:**
    * **Accuracy Treino:** 57% (caiu de 95%) -> **Overfitting Eliminado!**
    * **Accuracy Teste:** 57% (subiu de 52%) -> **Melhoria Real!**
  * **ConclusÃ£o:** O modelo estÃ¡ agora estÃ¡vel e generaliza bem. A performance (57%) igualou a RegressÃ£o LogÃ­stica, o que indica que atingimos o limite das features atuais. O modelo continua a nÃ£o conseguir prever Empates (Recall 0.00).

## 2025-12-27
  - Como a Professora tinha referido deveria tentar arranjar os dados dos clubes que sÃ£o promovidos da liga 2 para preencher os dados em falta.
  - Resultado: A fonte `football-data.co.uk` nÃ£o disponibiliza dados da Segunda Liga Portuguesa
  - DecisÃ£o: Manter a estratÃ©gia de imputaÃ§Ã£o (mÃ©dia das 3 piores equipas da Ã©poca anterior) para evitar atrasos com novos scrapers. O foco serÃ¡ criar features de "Forma Recente".

## 2025-12-31
- **[TESTE: REMOVER ODDS]**
  * Removi as Odds das features para ver se "estragavam" o modelo.
  * **Resultado Surpreendente:** A Accuracy manteve-se exatamente em 57% sem Odds!
  * **ConclusÃ£o:** As features estatÃ­sticas jÃ¡ capturam a mesma informaÃ§Ã£o que as odds. O problema nÃ£o Ã© "Odds vs Stats", Ã© o desequilÃ­brio de classes (ninguÃ©m acerta empates).

- **[FEATURE ENGINEERING 2.0]**
  * Adicionei novas mÃ©tricas avanÃ§adas que estavam adormecidas no dataset: xG (Golos Esperados), Posse de Bola, Passes Progressivos e, crucialmente, **"Forma de Empates"** (quantos empates a equipa teve nos Ãºltimos 5 jogos).
  * `Home_hist_PassesProgressivos` mostrou-se logo uma das TOP 10 features mais importantes.

- **[ESTRATÃ‰GIA "BALANCED" (O Pulo do Gato)]**
  * Para resolver o problema de "Recall 0.00" nos Empates, usei `class_weight='balanced'` no XGBoost.
  * **Antes:** 9% de acerto em Empates.
  * **Depois:** **47% de acerto em Empates!**
  * **Trade-off:** A Accuracy geral caiu para 49%, mas o modelo tornou-se muito mais Ãºtil para apostas, pois agora identifica oportunidades de odd alta (Empates) em vez de jogar sempre nos favoritos.
  * Criei o notebook `Modelacao_XGBoost_Balanced.ipynb` para consolidar esta nova abordagem.

## 2026-01-07
- **[SMOTE IMPLEMENTATION]**
  - Substitui o mÃ©todo de `sample_weights` por `SMOTE` (Synthetic Minority Over-sampling Technique) para lidar com o desequilÃ­brio de classes.
  - O objetivo Ã© gerar dados sintÃ©ticos para os empates em vez de apenas dar pesos maiores.
  - O objetivo Ã© gerar dados sintÃ©ticos para os empates em vez de apenas dar pesos maiores.

## 2026-01-08
  - Atualizei o notebook `Modelacao_XGBoost_Balanced.ipynb` com a nova implementaÃ§Ã£o.
  - **Resultados SMOTE:**
    * **Accuracy:** 51% (Melhor que Balanced Weights 49%, pior que Baseline 57%)
    * **Draw Recall:** 24% (Pior que Balanced Weights 47%, melhor que Baseline 0%)
    * **ConclusÃ£o:** O SMOTE Ã© um meio-termo. NÃ£o sacrifica tanto a accuracy geral como o `class_weight='balanced'`, mas tambÃ©m nÃ£o recupera tantos empates. Parece que simplesmente "forÃ§ar" o modelo a ver mais empates (Sample Weights) foi mais eficaz para o objetivo especÃ­fico de apanhar empates, mesmo com mais falsos positivos.
  - Criei um notebook separado `Modelacao_XGBoost_ClassWeight.ipynb` para manter a versÃ£o com `compute_sample_weight`, permitindo comparar diretamente com a versÃ£o SMOTE (`Modelacao_XGBoost_Balanced.ipynb`).

  - **[CLASS WEIGHT VS SMOTE: VERIFICATION & CONCLUSION]**
    - Executei um script de reproduÃ§Ã£o para validar a abordagem `class_weight='balanced'`.
    - **Resultados Confirmados:**
      * **Class Weight:** Accuracy **49%**, Draw Recall **47%**.
      * **SMOTE:** Accuracy **51%**, Draw Recall **24%**.
    - **Trade-off:**
      * A abordagem **Class Weight** forÃ§a o modelo a "arriscar" muito mais nos empates. Isso resulta em muitos mais acertos nessa classe (47% vs 24%), mas Ã  custa de errar mais nas previsÃµes de vitÃ³rias "fÃ¡ceis", baixando a accuracy global.
      * O **SMOTE** cria uma fronteira de decisÃ£o mais conservadora.
    - **DecisÃ£o:** Para o objetivo de maximizar o lucro em apostas de empate (que tÃªm odds altas), a abordagem **Class Weight** parece superior apesar da menor accuracy, pois captura quase o dobro dos empates. Manteremos ambos os notebooks para referÃªncia.

## 2026-01-10

- **[RANDOM FOREST IMPLEMENTATION]**
  - Implementei um modelo de `RandomForestClassifier` para comparar com o XGBoost, usando o mesmo setup:
    - Features: Set AvanÃ§ado (xG, Posse, Forma, etc.)
    - Class Weight: `balanced`
  - **Resultados Surpreendentes:**
    * **Accuracy:** **50.1%** (Ligeiramente superior ao XGBoost Class Weight de 49.3%)
    * **Draw Recall:** **48%** (Superior ao XGBoost Class Weight de 47%)
  - **ConclusÃ£o:** O Random Forest mostrou-se o modelo mais equilibrado atÃ© agora para o nosso objetivo especÃ­fico. Conseguiu nÃ£o sÃ³ manter a elevada taxa de deteÃ§Ã£o de empates (que Ã© o nosso foco para odds altas), como ainda melhorou ligeiramente a accuracy geral face Ã  abordagem de Class Weight do XGBoost.
  - **AÃ§Ã£o:** O notebook `Modelacao_RandomForest.ipynb` fica como uma alternativa muito forte para a estratÃ©gia de apostas em empates.

## 2026-01-10
  -  

## 2026-03-03

- **[CORREÇÃO DE DATA LEAKAGE]**
  * Descobri que o \	rain_test_split\ do meu Random Forest e XGBoost com \
andom_state=42\ estava a causar data leakage severo nas minhas estimativas, pois estava a baralhar as datas e a prever o passado usando dados do futuro. 
  * Quando passei a usar o correto \shuffle=False\, a Accuracy caiu para valores mais realistas (0.49). Isto foi um choque de realidade importante.
- **[CRIAR FEATURES AVANÇADAS]**
  * Decidi atacar o \dataset_final_merged_v2.csv\ e criar 4 tipos de variávies de alto nível através de um novo script (\feature_engineering.py\).
  * **1. ELO Rating Dinâmico:** Criei um sistema ELO que soma e subtrai probabilidade de qualidade baseado na força de cada adversário invés de contar apenas os pontos brutos.
  * **2. Expectativa de Golos (Poisson):** Usei um modelo matemático de ataque e defesa para que cada jogo diga qual a \Prob_Empate_Poisson\ exata. Perfeito para caçar empates chatos!
  * **3. Perfil de Risco (BTTS e Clean Sheets):** Adicionei as % dos últimos 5 jogos em que houve \Ambas Marcam\ e \Baliza a Zeros\ para ler tendências defensivas das equipas.
  * **4. Médias Móveis Autênticas:** Substitui os totais históricos vagos da época passada por \Rolling_5_Remates\ e \Rolling_5_Cantos\. Agora reflete exatamente o estado de forma da equipa na jornada atual!
  * **Resultados:** Com o Dataset de Features Avançadas, o novo \RandomForest\ treinado de forma limpa disparou a **Accuracy genuína e sem leakage para impressionantes 54%**, com um Recall brutal na classe \D\ (Empates) de **44%**! Finalmente consegui ultrapassar o teto antigo com dados matematicamente blindados.

  * **Nota sobre as Rolling Averages (vs Forma Recente):** Aprofundei o conceito que já tinha começado com as variáveis de forma (como \Casa_Form_Pts5\). Enquanto que as variáveis originais calculam a eficácia em *Tabela* da equipa (Pontos, Vitórias, Golos) nos últimos 5 jogos, estas novas \Rolling_5\ aplicam exatamente a mesma janela temporal mas às **estatísticas de desempenho em campo** (ex: número de Remates, Remates à Baliza, Cantos a favor). Isto dá ao modelo a capacidade de ler a narrativa do jogo e ver se uma equipa está a exercer pressão ofensiva, mesmo nos jogos em que teve azar e perdeu pontos na mesma.

  * **Nota sobre a Janela Temporal e as velhas Form5:** Apercebi-me também de um pormenor importante sobre o meu modelo anterior. Eu tinha estipulado a regra de 'strict temporal hold' (só usar dados fechados da época passada para o FBRef), mas as minhas próprias variáveis de \Casa_Form_Pts5\ já quebravam esta regra, porque olhavam para os 5 jogos da época *atual*. Afinal, a semente da solução atual já lá estava! Decidi assumir esta quebra de vez: abandonamos as estastísticas mortas do ano anterior e passamos a calcular tudo (incluindo as variáveis FBRef) usando a janela dos últimos 5 jogos da época corrente, o que nos colou finalmente à verdadeira forma atual das equipas.

## 2026-03-30

- **[TEMPORAL ROLLOUT - PREVISÃO JORNADA A JORNADA]**
  * A minha professora chamou-me a atenção (e bem) de que fazer predict a test_df (época inteira) num só `.predict()` gera um efeito "bola de neve" enorme quando depois tentamos extrapolar a tabela final do campeonato.
  * Estruturei uma nova lógica de previsão baseada em "Temporal Rollout":
    1. Agrupo o conjunto de dados da época de teste pelas Jornadas.
    2. No arranque da jornada: O modelo prevê os resultados dessa semana e uso essas previsões + simulações dos restantes jogos em falta para prever quem irá ser o campeão (usando os pontos consolidados até àquela data na tabela real).
    3. No final da mesma jornada: Os resultados REAIS ocorridos nesses jogos são revelados ao modelo (fundidos no `train_df`) e rodo novamente um `.fit()`.
  * Ganho de Realismo: O modelo nunca prevê uma ronda numa linha temporal alternativa cega, ajustando a sua experiência iterativamente à forma autêntica com que as equipas realmente jogaram nessas mesmas jornadas ao longo do ano.
  * **[IMPLEMENTAÇÃO TÉCNICA E SETUP DO NOTEBOOK]**
    * Deteção de falha no dataset alvo: o ficheiro `dataset_features_avancadas.csv` apenas possuía a "Data" pelo que desenvolvi e incorporei internamente o processo de agrupamento dinâmico que cria a `Epoca` (Jul-Jun) e a verdadeira `Jornada` de campeonato analisando o número de jogos passados de cada dupla de equipas num duelo.
    * O ficheiro **`Notebooks/Modelacao_Temporal_Rollout.ipynb`** foi criado na íntegra para testar este paradigma metodológico.
    * Preserva exatamente as mesmas **48 features de simulação super-avançadas** (Poisson, Elo, xG, Rolling Averages).
    * **[CORREÇÃO DE BUG: Acumulação de Pontos entre Épocas]**
      * Detetei visualmente que a abordagem de *split* cronológica de 80/20 (`int(len(df) * 0.8)`) enviesou o Notebook original ao integrar múltiplas épocas desportivas dispares dentro do próprio `test_df`. Isto causou uma anomalia na agregação da variável estática `Jornada`, em que o ciclo iterava e simulava os jogos de anos diferentes ao mesmo tempo, somando infinitamente pontos inter-épocas à mesma tabela classificativa (resultando num suposto Campeão com mais de 200 pontos no final da época de teste).
      * **Resolução Escrita**: A divisão *hardcoded* de percentagens foi removida a favor de um filtro restrito e orgânico. O `train_df` assimilou nativamente o histórico onde a `Epoca != 2023-2024`, e isolou-se de forma absoluta e asséptica a Época **2023-2024** para o `test_df`.
    * Mantém a modelação ideal que focava na melhor identificação dos lucros em odds altas (Empates): `RandomForestClassifier(class_weight='balanced', max_depth=10, n_estimators=100)`.
    * O Pipeline culmina agora devolvendo a Accuracy Real estática bem como a re-visualização da Matriz de Confusão e listando de forma linearmente contida os 80-90 pts orgânicos do pretenso campeão da Época 23/24 no fecho de cada ronda.

## 2026-04-13

- **[RANDOM FOREST - PIPELINE DE PREVISÃO DE JOGOS]**
  * Consolidei a pipeline de previsão com Random Forest e criei notebooks/utilitários de apoio para trabalhar jornada a jornada.
  * Atualizei o dataset `dataset_final_merged_v2.csv` para suportar o fluxo de treino/validação e as features necessárias.
  * Scripts auxiliares como o `add_jornada.py` ajudam a garantir que a identificação de `Jornada`/ordenação temporal fica consistente.

- **[SIMULAÇÃO MONTE CARLO - PROBABILIDADE DE CAMPEÃO]**
  * Criei o script `Notebooks/Simulacao_MonteCarlo.py` para simular múltiplos cenários de resultados (usando previsões do Random Forest) e estimar probabilidades de título ao longo da época.
  * Objetivo: transformar previsões de jogos isolados numa estimativa agregada (e mais interpretável) do desfecho do campeonato.

## 2026-05-19

- **[LIGA PREDICTOR WEB APPLICATION]**
  * Iniciei a transformação do projeto (anteriormente baseado em scripts Python de simulação Monte Carlo) num Dashboard Web interativo e responsivo.
  * O backend foi desenvolvido utilizando **FastAPI** para servir a simulação e expor os resultados.
  * O frontend é uma **Single Page Application (SPA)** nativa com HTML, CSS e Vanilla JavaScript. O dashboard permite configurar dinamicamente parâmetros como a jornada de início e o número de iterações da simulação.

- **[VISUALIZAÇÃO DE FEATURE IMPORTANCE]**
  * Implementada a capacidade de comunicar e renderizar as "Variáveis Mais Importantes do Modelo" no frontend. Os dados e métricas provêm do backend e são atualizados visualmente consoante o contexto da simulação.

- **[FEATURE DECAY LOGIC - GESTÃO DAS PRIMEIRAS JORNADAS]**
  * Diagnóstico: Nas primeiras jornadas (ex: Jornada 1), o modelo sentia falta de dados autênticos da forma atual ("últimos 5 jogos"), o que afetava a fiabilidade e gerava ruído.
  * Correção: Introdução de uma mecânica de **"Feature Decay"**. Agora, o backend ajusta o peso das variáveis (`rolling features`) de forma progressiva. No arranque do campeonato, o modelo confia predominantemente nos dados agregados da época transata (N-1). À medida que a época avança, o peso transita organicamente para os dados recentes de performance em tempo real.
  * O frontend foi atualizado para comunicar claramente o estado deste "decay", garantindo transparência ao utilizador quanto à origem da predição em diferentes momentos da época.

## 2026-05-20

- **[MONTE CARLO MULTIÉPOCA & RESILIÊNCIA DE ENCODING]**
  * Adaptei o motor de simulação Monte Carlo (`app/monte_carlo.py`) e endpoints da API (`app/api.py`) para suportar a seleção e simulação de qualquer época dinâmica presente no dataset (desde `2017-2018` até `2025-2026`).
  * Adicionei um dropdown de seleção de época responsivo no painel de controlo da interface web (`app/static/index.html` e `app/static/app.js`), que atualiza automaticamente as jornadas e equipas em tempo real.
  * Resolvi um conflito de codificação de caracteres especiais (ex: `ç` em `DiferençaDeGolos` e `ó` em `Vitórias`) aplicando `encoding='utf-8'` com `encoding_errors='replace'` na leitura do app.
  * Executei com sucesso o pipeline de ETL completo (`pipeline/run_all.py`), sincronizando ambos os datasets final e de features avançadas com exatamente 4.632 linhas de dados históricos e recentes.

- **[ANÁLISE E OTIMIZAÇÃO DO RANDOM FOREST]**
  * Realizei uma análise exaustiva e otimização hiperparamétrica sistemática do `RandomForestClassifier` com foco em calibração para Monte Carlo.
  * Executei uma pesquisa (`RandomizedSearchCV` com `TimeSeriesSplit`) comparando diferentes métricas de otimização (Accuracy vs F1-Macro vs Log Loss).
  * Descobri e documentei no ficheiro `analysis_results.md` a "Armadilha da Accuracy Pura", que aumentava a accuracy mas destruía o recall de empates (Recall 0%) ao ignorar a classe minoritária.
  * Escolhi e apliquei a configuração otimizada por **Log Loss** (`max_depth=4`, `min_samples_leaf=8`, `min_samples_split=10`, `max_features=0.2` e `class_weight='balanced'`), que evita overfitting e suaviza previsões probabilísticas.
  * Atualizei o modelo nos ficheiros principais (`app/monte_carlo.py`, `Notebooks/Simulacao_MonteCarlo.py` e `Notebooks/Modelacao_RandomForest.py`) e corrigi erros latentes de codificação de caracteres que impediam a execução direta em Windows.

- **[SISTEMA DE MÉTRICAS E VALIDAÇÃO DE PREVISÕES (ACCURACY & RECALL)]**
  * Desenvolvi no backend (`app/monte_carlo.py`) a lógica de avaliação das previsões para os jogos passados disputados na época selecionada. Sempre que a jornada alvo for superior a 1, o modelo calcula o *Accuracy* geral e o *Recall* (Sensibilidade) específico para cada desfecho desportivo (Vitória em Casa `H`, Empate `D`, Vitória Fora `A`).
  * Construí no frontend um painel de controlo premium de métricas (`#metrics-section` em `index.html`, `app.js` e `styles.css`) com estilo glassmorphic escuro, barras de progresso dinâmicas e indicadores visuais que reagem com micro-animações interativas e transições suaves após a execução da simulação.

- **[NORMALIZAÇÃO ROBUSTA DE ENCODINGS & MOJIBAKE]**
  * Detetei que o dataset principal continha um formato híbrido de dados, misturando linhas em UTF-8 e Latin-1. Esta inconsistência provocava caracteres corrompidos com o símbolo de substituição `` (como "Vitria" ou "Famalico") ou causava *mojibake* dupla-codificação ("VitÃ³ria").
  * Criei a função heurística `fix_mojibake` que reconverte dados distorcidos ao descodificar e recodificar condicionalmente os bytes de forma dinâmica e segura.
  * Integrei este corretor na leitura de dados em `app/monte_carlo.py`, `Notebooks/Simulacao_MonteCarlo.py` e `Notebooks/Modelacao_RandomForest.py`, limpando tanto os cabeçalhos das tabelas (o que preveniu `KeyErrors` críticos em colunas como `Home_hist_Vitórias`) como todas as colunas de texto (unificando e exibindo perfeitamente acentos portugueses nas equipas Vitória, Famalicão e Paços de Ferreira).

- **[DROPDOWN DE SELEÇÃO DE MODELO DE ML]**
  * Implementei um dropdown no Painel de Controlo que permite escolher dinamicamente o classificador de Machine Learning para a simulação Monte Carlo, com base nos notebooks criados no projeto.
  * **Modelos disponíveis:** Random Forest (padrão), XGBoost, Decision Tree e Regressão Logística.
  * **Backend (`app/monte_carlo.py`):** Adicionadas importações de `DecisionTreeClassifier`, `LogisticRegression` e `XGBClassifier`. A função `run_simulation()` recebe agora o parâmetro `modelo_alvo` e treina condicionalmente o classificador selecionado com os hiperparâmetros extraídos dos notebooks do projeto.
  * **Hiperparâmetros configurados:**
    - *XGBoost:* `learning_rate=0.05`, `max_depth=4`, `n_estimators=100`, `eval_metric='mlogloss'`, com `compute_sample_weight(class_weight='balanced')`.
    - *Decision Tree:* `max_depth=4`, `class_weight='balanced'`.
    - *Regressão Logística:* `solver='lbfgs'`, `max_iter=1000`, `class_weight='balanced'`.
  * **Feature Importance para Regressão Logística:** Modelos lineares não possuem `.feature_importances_`. Implementei um proxy baseado na média dos valores absolutos dos coeficientes: `importances = np.mean(np.abs(model.coef_), axis=0)`, que se integra perfeitamente nos gráficos de barras do frontend.
  * **API (`app/api.py`):** Campo `modelo` adicionado ao schema Pydantic `SimulationRequest` e propagado à chamada do backend.
  * **Frontend (`app.js`):** O modelo selecionado é enviado no payload JSON do POST, a mensagem de loading adapta-se dinamicamente ao nome do modelo, e as legendas das secções de métricas e feature importance atualizam-se automaticamente.
  * **Dependência:** Registado `xgboost` no `requirements.txt`.

- **[CORREÇÃO DE DATA LEAKAGE NAS MÉTRICAS DE VALIDAÇÃO]**
  * Identifiquei um problema crítico de Data Leakage no cálculo das métricas de validação ("Desempenho de Validação do Modelo"). O modelo principal, treinado com os jogos passados da época alvo incluídos no conjunto de treino, era usado para prever esses mesmos jogos passados. Isto resultava em accuracy inflacionada artificialmente (71.9% com XGBoost na época 2025-2026, quando o valor real out-of-sample é ~54%).
  * **Correção:** Criei um modelo de validação auxiliar (`model_val`) treinado exclusivamente nas épocas anteriores (excluindo toda a época alvo), que é usado apenas para calcular as métricas de Accuracy e Recall nos jogos passados. O modelo principal de simulação continua a usar toda a informação disponível para prever os jogos futuros.
  * **Resultados corrigidos (out-of-sample, época 2025-2026, jornada 17):**
    - Random Forest: 56.1% accuracy
    - XGBoost: 54.0% accuracy
    - Decision Tree: 54.0% accuracy
    - Regressão Logística: 54.0% accuracy
  * Estes valores situam-se na faixa realista de 54%-56%, consistente com a literatura e os resultados dos nossos notebooks.

- **[CORREÇÃO DE ERRO DE SERIALIZAÇÃO JSON (numpy.float32)]**
  * Identificado e corrigido um bug que causava HTTP 500 ao simular com XGBoost. O array `.feature_importances_` do scikit-learn/XGBoost armazena valores como `numpy.float32`, que não são serializáveis nativamente pelo `json.dumps()` do FastAPI.
  * Correção: cast explícito `float()` no cálculo percentual de importância de cada feature em `app/monte_carlo.py`.
  * Adicionalmente, melhorei o tratamento de erros no frontend (`app.js`) para lidar graciosamente com respostas HTTP 500 não-JSON, mostrando uma mensagem amigável em vez do erro críptico `JSON.parse: unexpected character`.

- **[REDESIGN DO PAINEL DE CONTROLO]**
  * Redesenhei por completo o Painel de Controlo da aplicação para uma estética mais premium e funcional.
  * **Cards individuais:** Cada parâmetro (Jornada, Simulações, Época, Modelo) vive agora dentro da sua própria card com fundo subtil, bordo e efeito hover interativo verde.
  * **Header com identidade:** O título do painel includes agora um ícone emoldurado e um subtítulo descritivo, separados dos controlos por uma linha divisória.
  * **Ícones contextuais:** Cada card tem o seu próprio ícone (📅 Jornada, 🔄 Simulações, 🏟️ Época, 🧠 Modelo).
  * **Tipografia corrigida:** Os valores numéricos usam `1.7rem`, enquanto nomes de modelos longos (como "Random Forest") usam uma variante menor (`1.25rem`) para nunca quebrar em duas linhas.
  * **Dropdowns premium:** Seta SVG customizada, focus ring com dupla camada, e emojis nos nomes dos modelos (🌲 🌳 ⚡ 📈).
  * **Grid 2×2:** Substituída a grelha de 4 colunas estreitas por 2×2 em desktop, dando mais espaço horizontal a cada controlo.
  * **Linha gradiente decorativa:** `::before` pseudo-elemento com gradiente verde-dourado de 2px no topo do painel.

## 2026-06-09

- **[REUNIÃO DE REQUISITOS - PIPELINE DINÂMICO SEMANAL]**
  * Numa reunião de alinhamento, confirmou-se que o site `footballdata.co.uk` disponibiliza atualizações de jogos jornada a jornada. Isto invalidou o requisito inicial do utilizador ter que introduzir dados manualmente a cada semana para a nova época `2026-2027`.
  * Decidimos adaptar a frequência do pipeline de dados para ser executado semanalmente de forma a obter os resultados das partidas recentes automaticamente, atualizando a simulação e os modelos sem qualquer intervenção do utilizador.

- **[GERAÇÃO DINÂMICA DE ÉPOCAS]**
  * Modifiquei o script [run_all.py](file:///d:/Diogo/Ambiente de Trabalho/PROJETO/pipeline/run_all.py) substituindo a lista estática de épocas pela função `get_seasons_to_process()`. A lista é agora calculada automaticamente com base no calendário civil (começando em `2425` até à época corrente ou época futura a iniciar).
  * Incorporei uma verificação de segurança no pipeline (`df_fd.empty`) para que, caso a época futura (ex: `2627`) ainda não tenha jogos ou calendário oficial publicado, o pipeline ignore essa época graciosamente sem causar erros de execução.

- **[AGENDAMENTO AUTOMÁTICO SEMANAL (GITHUB ACTIONS)]**
  * Atualizei o ficheiro de configuração do CI/CD [update_data.yml](file:///d:/Diogo/Ambiente de Trabalho/PROJETO/.github/workflows/update_data.yml) alterando o cron de execução anual para um agendamento semanal (todas as segundas e terças-feiras às 08:00 UTC). Isto cobre todos os desfechos dos fins de semana e segundas-feiras à noite, atualizando a base de dados.

- **[CORREÇÃO DE BUG PANDAS: KEYERROR 'SEASON']**
  * Identifiquei e corrigi um bug no cálculo de features avançadas em [features_avancadas.py](file:///d:/Diogo/Ambiente de Trabalho/PROJETO/pipeline/features_avancadas.py), onde a coluna `Season` era eliminada durante a operação `groupby().apply()` dependendo da versão do Pandas instalada. Adicionei lógica de restauração segura após o agrupamento temporal.
  * Testei o pipeline localmente e verifiquei o funcionamento correto: processou as épocas passadas, ignorou graciosamente a época `2026-2027` (por ainda não ter começado) e completou a sincronização de features avançadas com sucesso.


