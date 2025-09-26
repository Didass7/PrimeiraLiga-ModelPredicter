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