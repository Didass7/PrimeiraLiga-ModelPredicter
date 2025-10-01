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