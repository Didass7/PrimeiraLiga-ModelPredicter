# Previsão do Vencedor da Primeira Liga com Machine Learning

Este projeto, desenvolvido no âmbito da Licenciatura em Engenharia Informática, foca-se na aplicação de técnicas de *Data Science* e *Machine Learning* para prever o vencedor da Primeira Liga portuguesa de futebol.

## 📖 Descrição

O futebol é um fenómeno de grande impacto social e económico em Portugal, e a previsão de resultados desportivos é um desafio complexo que envolve lidar com múltiplas variáveis e a imprevisibilidade inerente ao jogo.

Este projeto visa desenvolver um modelo preditivo robusto, utilizando um vasto conjunto de dados históricos de desempenho das equipas. A aplicabilidade prática deste trabalho estende-se a diversas áreas como o jornalismo desportivo, plataformas de análise estatística e até clubes de futebol.

## 🎯 Objetivos

O principal objetivo é desenvolver um modelo de *Machine Learning* capaz de projetar os resultados de uma temporada e estimar a equipa com maior probabilidade de se sagrar campeã da Liga portuguesa.

## 📊 Dataset

Os dados foram recolhidos do site **FBref** ([fbref.com](https://fbref.com/en/)), uma fonte robusta que disponibiliza estatísticas detalhadas de mais de 20 épocas da Primeira Liga.

O processo de extração foi automatizado com um script em Python que utiliza **Selenium** para navegar nas páginas de cada época e **Pandas** para extrair e estruturar os dados.

O dataset final consolida 12 tabelas por época, abrangendo diversas métricas, tais como:
* **Estatísticas Gerais:** Pontos, Vitórias, Empates, Derrotas, Golos Marcados/Sofridos.
* **Estatísticas Avançadas:** *Expected Goals* (xG), *Expected Goals Against* (xGA), Ações que Criam Remates (SCA) e Golos (GCA).
* **Desempenho Específico:** Métricas de Guarda-redes, Remates, Passes, Ações Defensivas e Posse de Bola.
