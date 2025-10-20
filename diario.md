# Diário de Desenvolvimento – Projeto Liga Portuguesa ML

## 2025-09-24

- Pesquisei sites com datasets de interesse para o projeto; encontrei o FBref ([fbref.com](https://fbref.com/en/)) como o mais adequado e robusto.
- Analisei que o FBref tem todo o tipo de informações das ultimas 25 épocas da Liga Portuguesa com 12 tabelas por época
- Pesquisei formas de dar scrapping às tabelas que existem no website
- Recolhi a estrutura das tabelas do FBref e analisei quais colunas seriam mais relevantes para o projeto
- Comecei a planear o dataset bruto (todas as tabelas juntas)
- Cheguei à conclusão que o site que quero usar tem proteção contra scrapping por isso terei que retirar a informação de forma manual

## 2025-09-25

- Tradução do nome das colunas no plano do Dataset Final para generalizar todas as colunas de todas as tabelas para depois unir tudo.
- Extração de todas as tabelas da época 2024-2025
- Código base para extrair as tabelas de cada época, só é preciso trocar o link para cada ano
- Criado um Dataset Completo com todas as colunas de todas as tabelas da época 2024-2025
- Problemas com colunas repetidas

## 2025-09-28

- Problema com colunas repetidas resolvido (havia colunas com nomes identicos ex: Assistencias e Assistências)
- Criei pastas para as últimas 20 épocas, penso que seja o suficiente para realizar a previsão

## 2025-09-30

- Notei que quanto menos recente a epoca for menos informação o website tem.
- Comecei a tirar os dados da época 2023-24
- Fartei-me de fazer tudo manualmente e decidi voltar a pesquisar por formas de fazer isto automáticamente
- Descubri uma biblioteca chamada Selenium que dá para simular um navegador real e contornar as proteçoes do site
- Criei um script básico para tentar automatizar a navegação para a página de cada época e extrair as tabelas
- Alguns problemas que tive para épocas mais antigas:
  * Faltavam colunas de estatística como xG
  * Epocas com menos tabelas que as mais recentes
  * Erros com o merge por causa de dados inconsistentes na coluna 'Equipa'

## 2025-10-01

- Melhorei o script para prevenir erros para extrair apenas os dados existentes em cada época
- Adicionei lógica para saltar tabelas em falta sem interromper a extração
- Acabei a fase de recolha de dados com a geração do ficheiro data_completo.csv com as ultimas 20 épocas
- Comecei a limpar dados do dataset (colunas duplicadas)
- Terminei a limpeza do dataset e renomei clubes com nomes iguais como 'Gil Vicente' e 'Gil Vicente FC'
- Acabei agora de recolher todos os dados que preciso para realizar o projeto

## 2025-10-11

- Comecei a fazer o relatorio
- Escrevi a Introdução
- Comecei a pesquisar artigos e trabalhos identicos para fazer o estado da arte
- A principal fonte que encontrei foi o football-data.co.uk, tem os dados da Liga em CSV com estatísticas de jogo e adds de apostas
- A segunda principal que encontrei foi o Kaggle, não me pareceu ser uma fonte muito viavel porcausa da qualidade e manutenção. Talvez seja útil mais para a frente para validação
- Pesquisei sites como OpenFootball e football-data.org. O formato de dados no OpenFootball não é por tabelas e o football-data.org funciona com um API com um nível gratuito limitado

## 2025-10-13

- Cheguei à conclusão que o football-data.co.uk seria provavelmente a melhor fonte de dados para começar
- O FBRef é uma boa fonte e tem dados que o football-data.co.uk não tem
- Se juntasse os dados dos dois poderia criar um conjunto de dados mais robusto

## 2025-10-15

- Hoje pesquisei por sites que tentam resolver o mesmo problema que eu
- Vi o site "The application of machine learning techniques for predicting football match outcomes: a review" deu-me uma visão dos algoritmos mais comuns (Poisson, Redes Neuronais) e falou sobre a dificuldade em prever empates
- Também vi o artigo sobre a Primeira Liga no Medium (Paulo Matos). Foi útil por ser algo focado na mesma liga que eu. Usou o FBRef e aplicou a Random Forest e XGBoost, falou também sobre a dificuldade de prever empates. Conseguiu atinger uma percentagem de certidão de 53% - 56%

## 2025-10-16

- Li outro artigo sobre Gradient Boosting (Lewandowsky & Chlebus, 2021). Reforçou a ideia que modelos de gradient boosting como XGBoost e CatBoost são o estado da arte para este tipo de problemas superando outras abordagens
- Cheguei à conclusão que os modelos de gradient boosting (XGBoost) são a minha melhor opção

## 2025-10-18

- Li uma Tese chamada "Football Match Prediction using Deep Learning" (Shah, 2017). Apresentou o uso de redes Neuronais Recorrentes (LSTMs) para capturar a natureza sequencial do desempenho das equipas só que usava dados que eram proprietários e melhores dos que temos acesso
- Vi uma Resivão de Bunker et al. (2024). Esta revisão mais recente concluiu que CNNs e LSTMs ainda não conseguiram superar consistentemente o desempenho dos modelos de gradient boost como XGBoost
- Conclusão do dia: Deep Learning não é tão eficiente como Gradient Boosting

## 2025-10-19

- Pesquisei aplicações com previsão desportiva
- Comecei pela NerdyTips que é uma aplicação que oferece alguma transparência sobre a sua tecnologia. Menciona um motor de IA baseado em Java ("NT Apex")
- A app Soccer Predictions Football AI e Sports AI são exemplos de advanced machine learning e não fornecem detalhes
- Vi também a app BettingPros E Action Network que são plataformas que têm previsões com análise de especialistas
- Conclui que as apps comerciais tem muito pouca transparencia técnica e isso torna-as uma fonte pouco fiavel para me guiar

## 2025-10-20

- Hoje pesquisei projetos que tentaram fazer o mesmo que eu no github
- O primeiro que chamou mais à atenção foi o dagbolade/all_leagues-_prediction. Pareceu ser o mais completo, usa gradient boosting e usa um sistema de rating Elo
- O segundo foi o pawelp0499/football-prediction-model. Usa uma abordagem mais simples com Regressão Logística Multinomial em R.
- Pelo que vi posso concluir que o padrão testado e comprovado foi o uso de Python, usando Pandas Scikit-learn/XGBoost para modelagem e Flask para uma possível API

## 2025-10-20

- Apos alguns dias a pesquisar fiz um mini resumo com o que conclui:
  * Dados: combinar football-data.co.uk com os dados do FBRef
  * Algoritmos: o modelo principal deve ser XGBoost e posso usar um modelo de Regressão Logistica para comparar
  * Ideias: Criar um sistema de rating Elo para medir a forma das equipas
  * Avaliação: Devo treinar em épocas passadas e testar nas mais recente para evitar data leakage. Devo usar F1-score para avaliar a previsão de empates e log-loss
- Posso começar a escrever o estado da arte no relatório 
