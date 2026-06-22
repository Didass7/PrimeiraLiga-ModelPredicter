# Dicionário de Dados - Dataset Final da Liga Portuguesa

Este documento descreve as colunas presentes no ficheiro `dataset_final_merged.csv`.
O dataset combina informações jogo-a-jogo (fonte: football-data.co.uk) com estatísticas históricas da época anterior (fonte: FBRef).

## Informação do Jogo (Base)
| Coluna Original | Novo Nome | Descrição |
| :--- | :--- | :--- |
| `Div` | `Divisao` | Divisão do campeonato (ex: P1). |
| `Date` | `Data` | Data do jogo. |
| `Time` | `Hora` | Hora do pontapé de saída. |
| `HomeTeam` | `Equipa_Casa` | Nome da equipa que joga em casa. |
| `AwayTeam` | `Equipa_Visitante` | Nome da equipa que joga fora. |
| `FTHG` | `Golos_Casa_Final` | Golos marcados pela equipa da casa no final do jogo. |
| `FTAG` | `Golos_Visitante_Final` | Golos marcados pela equipa visitante no final do jogo. |
| `FTR` | `Resultado_Final` | Resultado final ('H'=Casa, 'D'=Empate, 'A'=Visitante). |
| `HTHG` | `Golos_Casa_Intervalo` | Golos da casa ao intervalo. |
| `HTAG` | `Golos_Visitante_Intervalo` | Golos do visitante ao intervalo. |
| `HTR` | `Resultado_Intervalo` | Resultado ao intervalo. |
| `HS` | `Remates_Casa` | Total de remates da equipa da casa. |
| `AS` | `Remates_Visitante` | Total de remates da equipa visitante. |
| `HST` | `Remates_Alvo_Casa` | Remates à baliza (no alvo) da casa. |
| `AST` | `Remates_Alvo_Visitante` | Remates à baliza (no alvo) do visitante. |
| `HF` | `Faltas_Casa` | Total de faltas cometidas pela casa. |
| `AF` | `Faltas_Visitante` | Total de faltas cometidas pelo visitante. |
| `HC` | `Cantos_Casa` | Cantos a favor da casa. |
| `AC` | `Cantos_Visitante` | Cantos a favor do visitante. |
| `HY` | `Amarelos_Casa` | Cartões amarelos para a casa. |
| `AY` | `Amarelos_Visitante` | Cartões amarelos para o visitante. |
| `HR` | `Vermelhos_Casa` | Cartões vermelhos para a casa. |
| `AR` | `Vermelhos_Visitante` | Cartões vermelhos para o visitante. |

## Odds (Apostas) - Resultado Final (1X2)
Odds para vitória da Casa, Empate ou Visitante.
O padrão de nomeação é `Odd_[Resultado]_[CasaApostas]`.

**Casas de Apostas Mapeadas:**
*   `Bet365` (Bet365)
*   `BetWin` (Bwin)
*   `Interwetten`
*   `Ladbrokes`
*   `Sportingbet`
*   `WilliamHill`
*   `VCBet` (BetVictor antigo)
*   `Betfair`
*   `BetfairEx` (Betfair Exchange)
*   `Pinnacle`
*   `1xBet`
*   `BetMGM`
*   `Coral`
*   `BlueSquare`
*   `Gamebookers`
*   `StanJames`

**Agregadores:**
*   `Media` (Média de mercado)
*   `Maxima` (Melhor odd disponível)
*   `Betbrain` (Dados históricos de agregador)

## Odds - Mais/Menos 2.5 Golos
| Novo Nome (Exemplo) | Descrição |
| :--- | :--- |
| `Odd_Mais2.5_Bet365` | Odd para haver mais de 2.5 golos (Over 2.5). |
| `Odd_Menos2.5_Bet365` | Odd para haver menos de 2.5 golos (Under 2.5). |

## Odds - Handicap Asiático
| Novo Nome (Exemplo) | Descrição |
| :--- | :--- |
| `Handicap_Asiatico_Linha` | A linha de handicap (ex: -0.5, +1.0). |
| `Odd_Handicap_Casa_Bet365` | Odd para a equipa da casa cobrir o handicap. |
| `Odd_Handicap_Visitante_Bet365` | Odd para a equipa visitante cobrir o handicap. |

## Odds de Fecho (Closing Odds)
Odds registadas momentos antes do jogo começar. Têm o prefixo `Odd_Fecho_`.
Ex: `Odd_Fecho_Casa_Bet365`, `Odd_Fecho_Mais2.5_Pinnacle`.

## Betfair Exchange (Códigos Específicos)
Colunas específicas da Betfair Exchange (Intercâmbio).

| Coluna | Descrição |
| :--- | :--- |
| `BFEH`, `BFED`, `BFEA` | Odds Betfair Exchange para Casa (Home), Empate (Draw), Visitante (Away). |
| `BFDH`, `BFDD`, `BFDA` | *Dados adicionais Betfair Exchange (possivelmente variações ou volumes).* |
| `BFDCH`, `BFDCD`, `BFDCA` | *Dados adicionais Betfair Exchange (possivelmente variações ou volumes).* |
| `Odd_..._BetfairEx` | Odds de mercados específicos (Mais/Menos, Handicap) na Betfair Exchange. |
| `Odd_Fecho_..._BetfairEx` | Odds de fecho na Betfair Exchange. |

## Estatísticas Históricas (Contexto)
Estas colunas vêm do FBRef e referem-se à **época anterior**.
Estão divididas em `Home_hist_...` (para a equipa da casa) e `Away_hist_...` (para a equipa visitante).
*(Nota: Os prefixos mantiveram-se `Home_hist_` e `Away_hist_` para facilitar a identificação técnica, mas o conteúdo é histórico).*

Exemplos das principais métricas:
| Prefixo | Descrição |
| :--- | :--- |
| `Home_hist_Pontos` | Pontos conquistados pela equipa da casa na época anterior. |
| `Home_hist_GolosMarcados` | Total de golos marcados na época anterior. |
| `Home_hist_xG` | "Expected Goals" (Golos Esperados) na época anterior. |

### Categorias de Métricas FBRef
As métricas cobrem diversas áreas do jogo. Exemplos de sufixos comuns:

*   **Ataque:** `..._Remates`, `..._RematesÀBaliza`, `..._AcoesQueCriamRemates`, `..._GolosEsperados` (xG).
*   **Passe:** `..._PassesCompletos`, `..._PassesProgressivos`, `..._PassesChave`, `..._Assistencias`.
*   **Defesa:** `..._Desarmes`, `..._Intercecoes`, `..._Bloqueamentos`, `..._Alivios`, `..._Pressao`.
*   **Posse:** `..._PosseDeBola`, `..._ToquesNaBola`, `..._ConducoesProgressivas`.
*   **Geral:** `..._JogosDisputados`, `..._Vitórias`, `..._Empates`, `..._Derrotas`.

> **Nota:** Todas estas métricas são médias ou totais acumulados da **época anterior** à do jogo em questão. |

## Colunas Auxiliares
| Nome | Descrição |
| :--- | :--- |
| `Season` | Época do jogo (ex: "2023-2024"). |
| `Previous_Season` | Época anterior (usada para o merge). |
