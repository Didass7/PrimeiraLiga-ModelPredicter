import os
import time
import requests
import pandas as pd
import numpy as np
from io import StringIO

# Caminho absoluto para a base de dados local do FBRef
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FBREF_DATABASE_PATH = os.path.join(ROOT_DIR, "Datasets", "FBRef", "dataset_completo_final.csv")

def extract_football_data(season: str):
    """
    Faz o download automático dos dados da Primeira Liga do football-data.co.uk.
    O formato da season deve ser ex: '2425' ou '2526'.
    """
    url = f"https://www.football-data.co.uk/mmz4281/{season}/P1.csv"
    print(f"[Extract] A descarregar dados de Football-Data.co.uk de: {url}")
    try:
        df = pd.read_csv(url)
        print(f"[Extract] Download efetuado com sucesso! {len(df)} jogos encontrados.")
        return df
    except Exception as e:
        print(f"[Extract] Erro ao descarregar do Football-Data: {e}")
        return None

def extract_fbref(season: str):
    """
    Scraper robusto de Selenium do FBRef usando undetected-chromedriver.
    1. Verifica primeiro se a época já existe no banco de dados local.
    2. Se não existir, tenta raspar usando undetected-chromedriver.
       - Corre em modo Headless no GitHub Actions.
       - Corre em modo Não-Headless (Normal) localmente para facilitar a resolução do Turnstile da Cloudflare.
    3. Trata erros como 429 ou bloqueios de Cloudflare de forma graciosa (sem quebrar o pipeline).
    """
    try:
        epoca_inicio = 2000 + int(season[:2])
        epoca_fim = 2000 + int(season[2:])
        epoca_str = f"{epoca_inicio}-{epoca_fim}"
    except ValueError:
        print(f"[Extract] Formato de época inválido: {season}. Deve ser no formato '2425'.")
        return None

    print(f"[Extract] A verificar dados FBRef locais para a época {epoca_str}...")

    # 1. Tentar ler do banco de dados local primeiro
    if os.path.exists(FBREF_DATABASE_PATH):
        try:
            df_db = pd.read_csv(FBREF_DATABASE_PATH, encoding='latin1')
            if not df_db.empty and 'Epoca' in df_db.columns:
                df_season = df_db[df_db['Epoca'] == epoca_str]
                if not df_season.empty:
                    print(f"[Extract] Encontrados dados locais para {epoca_str} no cache! Carregamento concluído.")
                    return df_season
        except Exception as e:
            print(f"[Extract] Aviso: Falha ao ler cache local do FBRef: {e}. Avançando para raspagem...")

    # 2. Se não estiver no cache, tentar raspar
    print(f"[Extract] Dados da época {epoca_str} não encontrados localmente. A iniciar raspagem...")
    
    # Determinar se corre em headless ou normal
    is_github_actions = os.environ.get('GITHUB_ACTIONS') == 'true'
    
    # URLs a tentar: primeiro o específico, depois o genérico (fallback para a época corrente)
    urls_to_try = [
        f"https://fbref.com/en/comps/32/{epoca_str}/{epoca_str}-Primeira-Liga-Stats",
        "https://fbref.com/en/comps/32/Primeira-Liga-Stats"
    ]

    html_content = None
    
    try:
        import undetected_chromedriver as uc
        print("[Extract] Undetected-chromedriver importado com sucesso. Configurando driver...")
        
        options = uc.ChromeOptions()
        if is_github_actions:
            print("[Extract] Detetado ambiente GitHub Actions. Correndo em modo HEADLESS...")
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
        else:
            print("[Extract] Detetado ambiente LOCAL. Correndo em modo VISÍVEL (Não-Headless) para contornar Cloudflare...")
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')

        driver = uc.Chrome(options=options)
        
        for url in urls_to_try:
            print(f"[Extract] A tentar descarregar de: {url}")
            try:
                driver.get(url)
                # Espera 10 segundos para dar tempo à Cloudflare de validar a assinatura
                time.sleep(10)
                page_source = driver.page_source
                
                if "Cloudflare" in page_source:
                    print(f"[Extract] Bloqueado por Cloudflare no URL: {url}")
                    continue
                elif "429" in page_source or "Too Many Requests" in page_source:
                    print(f"[Extract] Bloqueado por taxa limite (429) no URL: {url}")
                    continue
                
                # Se passou as verificações e parece ter conteúdo
                if "Squad Standard Stats" in page_source or "Overall" in page_source:
                    html_content = page_source
                    print(f"[Extract] Sucesso ao carregar a página FBRef!")
                    break
            except Exception as url_err:
                print(f"[Extract] Erro ao carregar URL {url}: {url_err}")
                
        driver.quit()
        
    except Exception as driver_init_err:
        print(f"[Extract] Erro ao carregar undetected-chromedriver ou Selenium: {driver_init_err}")
        print("[Extract] Não foi possível iniciar o browser de raspagem.")

    # 3. Se conseguimos obter o HTML, processamos as tabelas
    if html_content is not None:
        try:
            tables = pd.read_html(StringIO(html_content))
            dataframes_processados = {}

            def limpar_colunas(df):
                df.columns = ["_".join([str(c).strip() for c in col if c]) if isinstance(col, tuple) else str(col).strip() for col in df.columns.values]
                return df

            def selecionar_colunas_existentes(df, colunas_desejadas):
                colunas_existentes = [col for col in colunas_desejadas if col in df.columns]
                return df[colunas_existentes]
            
            def processar_tabela_secundaria(tabela, renames_dict):
                df = limpar_colunas(tabela.copy())
                nome_coluna_equipa_original = df.columns[0]
                df = df.rename(columns={nome_coluna_equipa_original: 'Equipa'})
                df_selecionado = selecionar_colunas_existentes(df, list(renames_dict.keys()))
                df_final = df_selecionado.rename(columns=renames_dict)
                
                if 'Equipa' in df_final.columns:
                    df_final['Equipa'] = df_final['Equipa'].astype(str).str.strip()
                return df_final

            # Tabela Overall
            df_overall = tables[0].copy().rename(columns={'Squad': 'Equipa'})
            if 'Equipa' in df_overall.columns:
                df_overall['Equipa'] = df_overall['Equipa'].astype(str).str.strip()
            colunas_desejadas_overall = ['Equipa', 'MP', 'W', 'D', 'L', 'GF', 'GA', 'GD', 'Pts', 'xG', 'xGA', 'xGD']
            df_overall = selecionar_colunas_existentes(df_overall, colunas_desejadas_overall)
            df_overall = df_overall.rename(columns={
                'MP': 'JogosDisputados', 'W': 'Vitórias', 'D': 'Empates', 'L': 'Derrotas', 
                'GF': 'GolosMarcados', 'GA': 'GolosSofridos', 'GD': 'DiferençaDeGolos', 
                'Pts': 'Pontos', 'xG': 'GolosEsperados', 'xGA': 'GolosEsperadosSofridos', 
                'xGD': 'DiferençaDeGolosEsperados'
            })
            dataframes_processados['overall'] = df_overall

            # Tabelas Secundárias
            renames_map = {
                'stats': (2, {'Equipa': 'Equipa', 'Performance_Gls': 'Golos', 'Performance_Ast': 'Assistências', 'Performance_G+A': 'Golos+Assistências', 'Expected_xG': 'GolosEsperados', 'Expected_xAG': 'GolosEsperadosAssistidos', 'Expected_npxG': 'GolosEsperadosSemPenáltis', 'Progression_PrgC': 'ConduçõesProgressivas', 'Progression_PrgP': 'PassesProgressivos'}, "Squad Standard Stats"),
                'goalkeeping': (4, {'Equipa': 'Equipa', 'Performance_GA': 'GolosSofridos', 'Performance_CS': 'JogosSemSofrerGolos', 'Performance_CS%': '%DeJogosSemSofrerGolos', 'Performance_Save%': '%DeDefesas', 'Performance_SoTA': 'RematesÀBalizaSofridos'}, "Squad Goalkeeping"),
                'goalkeeping_advanced': (6, {'Equipa': 'Equipa', 'Expected_PSxG': 'GolosEsperadosAposRemate', 'Expected_PSxG+/-': 'GolosEsperadosAposRemate+/-', 'Sweeper_#OPA': 'AcoesForaDaGrandeArea'}, "Squad Advanced Goalkeeping"),
                'shooting': (8, {'Equipa': 'Equipa', 'Standard_Gls': 'Golos', 'Standard_Sh': 'Remates', 'Standard_SoT': 'RematesÀBaliza', 'Standard_SoT%': '%DeRematesÀBaliza', 'Expected_xG': 'GolosEsperados', 'Expected_npxG': 'GolosEsperadosSemPenáltis'}, "Squad Shooting"),
                'passing': (10, {'Equipa': 'Equipa', 'Total_Cmp%': '%DePassesCompletos', 'Total_TotDist': 'DistanciaTotalPercorrida', 'Total_PrgDist': 'DistanciaProgressivaPercorrida', 'Unnamed: 17_level_0_Ast': 'Assistencias', 'Unnamed: 18_level_0_xAG': 'GolosEsperadosAssistidos', 'Unnamed: 21_level_0_KP': 'PassesChave', 'Unnamed: 25_level_0_PrgP': 'PassesProgressivos'}, "Squad Passing"),
                'passing_types': (12, {'Equipa': 'Equipa', 'Unnamed: 3_level_0_Att': 'TentativasDePasse', 'Pass Types_TB': 'BolasEmProfundidade', 'Pass Types_Sw': 'InversoesDeJogo'}, "Squad Pass Types"),
                'gca': (14, {'Equipa': 'Equipa', 'SCA_SCA': 'AcoesQueCriamRemates', 'SCA_SCA90': 'AcoesQueCriamRematesPor90minutos', 'GCA_GCA': 'AcoesQueCriamGolos', 'GCA_GCA90': 'AcoesQueCriamGolosPor90minutos'}, "Squad Goal and Shot Creation"),
                'defensive': (16, {'Equipa': 'Equipa', 'Tackles_Tkl': 'Desarmes', 'Unnamed: 15_level_0_Int': 'Intercecoes', 'Blocks_Blocks': 'Bloqueamentos', 'Unnamed: 16_level_0_Tkl+Int': 'Desarmes+Intercecoes', 'Unnamed: 17_level_0_Clr': 'Alivios'}, "Squad Defensive Actions"),
                'possession': (18, {'Equipa': 'Equipa', 'Unnamed: 2_level_0_Poss': 'PosseDeBola', 'Touches_Touches': 'ToquesNaBola', 'Carries_PrgC': 'ConducoesProgressivas', 'Receiving_PrgR': 'RececoesProgressivas'}, "Squad Possession"),
                'success': (20, {'Equipa': 'Equipa', 'Team Success_+/-': 'SaldoDeGolos+/-', 'Team Success_+/-90': 'SaldoDeGolos+/-Por90minutos', 'Team Success (xG)_xG+/-': 'SaldoDeGolosEsperados+/-', 'Team Success (xG)_xG+/-90': 'SaldoDeGolosEsperados+/-Por90minutos'}, "Playing Time (Team Success)"),
                'misc': (22, {'Equipa': 'Equipa', 'Aerial Duels_Won%': '%DeDuelosAéreosGanhos'}, "Miscellaneous Stats")
            }

            for nome_df, (indice, renames, nome_legivel) in renames_map.items():
                try:
                    dataframes_processados[nome_df] = processar_tabela_secundaria(tables[indice], renames)
                except IndexError:
                    pass

            # Merge final
            lista_dfs_epoca = list(dataframes_processados.values())
            dataset_epoca = lista_dfs_epoca[0]
            for df_temp in lista_dfs_epoca[1:]:
                dataset_epoca = pd.merge(dataset_epoca, df_temp, on='Equipa', how='left')

            dataset_epoca['Epoca'] = epoca_str

            # Limpar duplicados
            cols_x = [c for c in dataset_epoca.columns if c.endswith('_x')]
            for col_x in cols_x:
                base_col = col_x[:-2]
                col_y = base_col + '_y'
                if col_y in dataset_epoca.columns:
                    dataset_epoca[base_col] = dataset_epoca[col_x].fillna(dataset_epoca[col_y])
                    dataset_epoca.drop(columns=[col_x, col_y], inplace=True)

            colunas_numericas = dataset_epoca.select_dtypes(include=np.number).columns.tolist()
            dataset_epoca[colunas_numericas] = dataset_epoca[colunas_numericas].fillna(0)

            # Normalização de nomes
            mapeamento_nomes = {
                'Gil Vicente FC': 'Gil Vicente',
                'B-SAD': 'Belenenses',
                'Sporting': 'Sporting CP'
            }
            dataset_epoca['Equipa'] = dataset_epoca['Equipa'].replace(mapeamento_nomes)

            # Guardar no cache local
            print(f"[Extract] A guardar dados no cache local: {FBREF_DATABASE_PATH}")
            os.makedirs(os.path.dirname(FBREF_DATABASE_PATH), exist_ok=True)
            
            if os.path.exists(FBREF_DATABASE_PATH):
                df_existente = pd.read_csv(FBREF_DATABASE_PATH, encoding='latin1')
                df_existente = df_existente[df_existente['Epoca'] != epoca_str]
                df_final_db = pd.concat([df_existente, dataset_epoca], ignore_index=True)
            else:
                df_final_db = dataset_epoca
                
            df_final_db.to_csv(FBREF_DATABASE_PATH, index=False, encoding='latin1')
            print("[Extract] Cache local de dados FBRef atualizado com sucesso!")
            
            return dataset_epoca

        except Exception as parse_err:
            print(f"[Extract] Erro ao parsear tabelas HTML do FBRef: {parse_err}")

    # 4. Caso de Falha de Raspagem Geral (Bypass falhou ou bloqueado por 429)
    print(f"\n[Extract] AVISO: Não foi possível descarregar dados novos do FBRef devido a limites de taxa/Cloudflare.")
    if is_github_actions:
        print("[Extract] DICA: Corre o pipeline localmente ('python pipeline/run_all.py') para atualizar o cache local")
        print("[Extract]       e faz o commit/push do ficheiro 'dataset_completo_final.csv' para o GitHub!")
    print("[Extract] O pipeline continuará usando o cache histórico existente e preenchimento por imputação.\n")
    
    return None

if __name__ == "__main__":
    print("Módulo de Extração do FBRef ativo.")
