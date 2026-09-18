import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import gspread
import html

from datetime import datetime
from google.oauth2.service_account import Credentials


# =========================================================
# CONFIGURAÇÃO
# =========================================================

st.set_page_config(
    page_title="Dashboard de Monitorias",
    page_icon="N",
    layout="wide"
)


# =========================================================
# PALETA
# =========================================================

BG = "#F6F7FB"
CARD = "#FFFFFF"
BORDER = "#E5E8F0"

TEXT = "#1F2937"
SECONDARY = "#6B7280"

PRIMARY = "#4361EE"
PRIMARY_SOFT = "#EEF2FF"

SUCCESS = "#059669"
SUCCESS_SOFT = "#ECFDF5"

WARNING = "#D97706"
WARNING_SOFT = "#FFFBEB"

CRITICAL = "#DC2626"
CRITICAL_SOFT = "#FEF2F2"

GRAY = "#CBD5E1"


# =========================================================
# CSS
# =========================================================

st.markdown(
    f"""
    <style>

    /* =====================================================
       BASE
       ===================================================== */

    @import url(
        'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
    );

    html,
    body,
    .stApp,
    [class*="st-"] {{
        font-family: 'Inter', sans-serif;
    }}

    .stApp {{
        background:
            radial-gradient(
                circle at 92% 0%,
                rgba(67, 97, 238, 0.055),
                transparent 28%
            ),
            {BG};
        color: {TEXT};
    }}

    .block-container {{
        max-width: 1440px;
        padding-top: 1.8rem;
        padding-bottom: 5rem;
    }}

    #MainMenu,
    footer {{
        visibility: hidden;
    }}

    [data-testid="stHeader"] {{
        background: transparent !important;
    }}

    /* =====================================================
       TIPOGRAFIA
       ===================================================== */

    h1 {{
        color: {TEXT} !important;
        font-size: 2rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.045em;
        margin-bottom: 3px !important;
    }}

    h2 {{
        color: {TEXT} !important;
        font-size: 1.25rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.025em;
        margin-top: 2.2rem !important;
        margin-bottom: 5px !important;
    }}

    h3 {{
        color: {TEXT} !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
    }}

    p {{
        color: {TEXT};
    }}

    .stCaption {{
        color: {SECONDARY} !important;
    }}

    .subtitle {{
        color: {SECONDARY};
        font-size: 14px;
        font-weight: 400;
        margin-top: 0;
        margin-bottom: 28px;
    }}

    .section-caption {{
        color: {SECONDARY};
        font-size: 13px;
        margin-top: -2px;
        margin-bottom: 17px;
    }}

    /* =====================================================
       SELECTBOX / FILTROS
       ===================================================== */

    div[data-baseweb="select"] {{
        width: 100%;
    }}

    div[data-baseweb="select"] > div {{
        background: {CARD} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 12px !important;
        min-height: 44px;
        box-shadow:
            0 1px 2px rgba(31, 41, 55, 0.025);
        transition:
            border-color 0.18s ease,
            box-shadow 0.18s ease;
    }}

    div[data-baseweb="select"] > div:hover {{
        border-color: rgba(67, 97, 238, 0.45) !important;
        box-shadow:
            0 3px 10px rgba(67, 97, 238, 0.07);
    }}

    div[data-baseweb="select"] [data-baseweb="icon"] {{
        color: {PRIMARY};
    }}

    label[data-testid="stWidgetLabel"] p {{
        color: {TEXT} !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        margin-bottom: 6px !important;
    }}

    /* =====================================================
       BOTÃO
       ===================================================== */

    .stButton > button {{
        background: {CARD} !important;
        color: {TEXT} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 11px !important;
        min-height: 42px;
        padding: 0 17px;
        font-weight: 600;
        font-size: 13px;
        box-shadow:
            0 1px 2px rgba(31, 41, 55, 0.03);
        transition:
            all 0.18s ease;
    }}

    .stButton > button:hover {{
        background: {PRIMARY_SOFT} !important;
        border-color: rgba(67, 97, 238, 0.35) !important;
        color: {PRIMARY} !important;
        transform: translateY(-1px);
        box-shadow:
            0 5px 14px rgba(67, 97, 238, 0.10);
    }}

    /* =====================================================
       CARD BASE
       ===================================================== */

    .custom-card {{
        position: relative;
        background: {CARD};
        border: 1px solid {BORDER};
        border-radius: 16px;
        padding: 22px;
        min-height: 132px;
        overflow: hidden;
        box-shadow:
            0 2px 5px rgba(31, 41, 55, 0.025),
            0 8px 24px rgba(31, 41, 55, 0.025);
        transition:
            transform 0.18s ease,
            box-shadow 0.18s ease,
            border-color 0.18s ease;
    }}

    .custom-card::before {{
        content: "";
        position: absolute;
        left: 0;
        top: 0;
        width: 4px;
        height: 100%;
        background: {PRIMARY};
        opacity: 0.9;
    }}

    .custom-card:hover {{
        transform: translateY(-2px);
        border-color: #D9DEEB;
        box-shadow:
            0 5px 12px rgba(31, 41, 55, 0.035),
            0 14px 30px rgba(31, 41, 55, 0.035);
    }}

    .custom-card-title {{
        color: {SECONDARY};
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.09em;
        margin-bottom: 13px;
    }}

    .custom-card-value {{
        color: {TEXT};
        font-size: 32px;
        font-weight: 800;
        line-height: 1;
        letter-spacing: -0.035em;
        font-variant-numeric: tabular-nums;
    }}

    .custom-card-subtitle {{
        color: {SECONDARY};
        font-size: 12px;
        margin-top: 10px;
    }}

    /* =====================================================
       PRAÇAS
       ===================================================== */

    .praca-card {{
        position: relative;
        background: linear-gradient(
            145deg,
            {CARD} 0%,
            #FAFBFF 100%
        );
        border: 1px solid {BORDER};
        border-radius: 16px;
        padding: 21px;
        min-height: 125px;
        overflow: hidden;
        box-shadow:
            0 2px 5px rgba(31, 41, 55, 0.025),
            0 8px 22px rgba(31, 41, 55, 0.025);
        transition:
            transform 0.18s ease,
            box-shadow 0.18s ease;
    }}

    .praca-card::after {{
        content: "";
        position: absolute;
        width: 70px;
        height: 70px;
        right: -24px;
        top: -24px;
        border-radius: 50%;
        background: {PRIMARY_SOFT};
    }}

    .praca-card:hover {{
        transform: translateY(-2px);
        box-shadow:
            0 8px 22px rgba(31, 41, 55, 0.06);
    }}

    .praca-name {{
        position: relative;
        z-index: 1;
        color: {TEXT};
        font-size: 20px;
        font-weight: 750;
        margin-bottom: 12px;
        letter-spacing: -0.025em;
    }}

    .praca-info {{
        position: relative;
        z-index: 1;
        color: {SECONDARY};
        font-size: 12px;
    }}

    /* =====================================================
       SCORE
       ===================================================== */

    .score-card {{
        position: relative;
        background:
            linear-gradient(
                145deg,
                #FFFFFF 0%,
                #F8F9FF 100%
            );
        border: 1px solid #DDE3F4;
        border-radius: 18px;
        padding: 30px;
        min-height: 250px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        overflow: hidden;
        box-shadow:
            0 4px 10px rgba(67, 97, 238, 0.035),
            0 16px 32px rgba(31, 41, 55, 0.035);
    }}

    .score-card::before {{
        content: "";
        position: absolute;
        width: 150px;
        height: 150px;
        right: -55px;
        top: -55px;
        border-radius: 50%;
        background: {PRIMARY_SOFT};
    }}

    .score-label {{
        position: relative;
        z-index: 1;
        color: {SECONDARY};
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.09em;
        margin-bottom: 13px;
    }}

    .score-value {{
        position: relative;
        z-index: 1;
        color: {TEXT};
        font-size: 46px;
        font-weight: 800;
        line-height: 1;
        letter-spacing: -0.04em;
        font-variant-numeric: tabular-nums;
    }}

    .score-description {{
        position: relative;
        z-index: 1;
        color: {SECONDARY};
        font-size: 12px;
        margin-top: 13px;
        line-height: 1.55;
        max-width: 280px;
    }}

    /* =====================================================
       EQUIPE
       ===================================================== */

    .team-card {{
        position: relative;
        background: {CARD};
        border: 1px solid {BORDER};
        border-radius: 16px;
        padding: 20px;
        min-height: 180px;
        overflow: hidden;
        box-shadow:
            0 2px 5px rgba(31, 41, 55, 0.025),
            0 8px 22px rgba(31, 41, 55, 0.025);
        transition:
            transform 0.18s ease,
            box-shadow 0.18s ease;
    }}

    .team-card:hover {{
        transform: translateY(-2px);
        box-shadow:
            0 8px 24px rgba(31, 41, 55, 0.055);
    }}

    .team-name {{
        color: {TEXT};
        font-size: 14px;
        font-weight: 700;
        margin-bottom: 15px;
        letter-spacing: -0.01em;
    }}

    .team-number {{
        color: {TEXT};
        font-size: 30px;
        font-weight: 800;
        line-height: 1;
        letter-spacing: -0.035em;
        font-variant-numeric: tabular-nums;
    }}

    .team-label {{
        color: {SECONDARY};
        font-size: 11px;
        margin-top: 5px;
    }}

    .team-progress {{
        width: 100%;
        height: 7px;
        background: #E9ECF3;
        border-radius: 99px;
        margin-top: 18px;
        overflow: hidden;
    }}

    .team-progress-fill {{
        height: 100%;
        background: linear-gradient(
            90deg,
            {PRIMARY},
            #5C75EE
        );
        border-radius: 99px;
        transition: width 0.4s ease;
    }}

    .team-status {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 10px;
        font-size: 11px;
    }}

    .team-realizada {{
        color: {SUCCESS};
        font-weight: 600;
    }}

    .team-pendente {{
        color: {WARNING};
        font-weight: 600;
    }}

    /* =====================================================
       LISTAS
       ===================================================== */

    .list-card {{
        background: {CARD};
        border: 1px solid {BORDER};
        border-radius: 16px;
        padding: 21px;
        min-height: 160px;
        box-shadow:
            0 2px 5px rgba(31, 41, 55, 0.025),
            0 8px 22px rgba(31, 41, 55, 0.025);
    }}

    .list-title {{
        color: {TEXT};
        font-size: 14px;
        font-weight: 700;
        margin-bottom: 13px;
        letter-spacing: -0.01em;
    }}

    .list-item {{
        border-bottom: 1px solid #EEF0F4;
        padding: 11px 0;
    }}

    .list-item:last-child {{
        border-bottom: none;
    }}

    .list-name {{
        color: {TEXT};
        font-size: 13px;
        font-weight: 600;
    }}

    .list-function {{
        color: {SECONDARY};
        font-size: 11px;
        margin-top: 3px;
    }}

    .list-score {{
        display: inline-block;
        color: {PRIMARY};
        background: {PRIMARY_SOFT};
        border-radius: 6px;
        padding: 3px 7px;
        font-size: 10px;
        font-weight: 700;
        margin-top: 5px;
        font-variant-numeric: tabular-nums;
    }}

    .empty-message {{
        color: {SECONDARY};
        font-size: 12px;
        padding: 12px 0;
    }}

    /* =====================================================
       STATUS
       ===================================================== */

    .badge {{
        display: inline-block;
        padding: 5px 9px;
        border-radius: 7px;
        font-size: 10px;
        font-weight: 700;
    }}

    .badge-success {{
        color: {SUCCESS};
        background: {SUCCESS_SOFT};
    }}

    .badge-warning {{
        color: {WARNING};
        background: {WARNING_SOFT};
    }}

    .badge-critical {{
        color: {CRITICAL};
        background: {CRITICAL_SOFT};
    }}

    /* =====================================================
       FILTRO ATIVO
       ===================================================== */

    .filter-summary {{
        background: linear-gradient(
            90deg,
            {PRIMARY_SOFT},
            #F8F9FF
        );
        border: 1px solid #DCE4FF;
        border-radius: 12px;
        padding: 12px 16px;
        margin-top: 8px;
        margin-bottom: 25px;
        color: {TEXT};
        font-size: 12px;
        box-shadow:
            0 3px 10px rgba(67, 97, 238, 0.035);
    }}

    .filter-summary strong {{
        color: {PRIMARY};
        font-weight: 700;
    }}

    /* =====================================================
       GRÁFICOS PLOTLY
       ===================================================== */

    .js-plotly-plot {{
        border-radius: 16px;
    }}

    /* =====================================================
       ESPAÇAMENTO
       ===================================================== */

    [data-testid="column"] {{
        padding-left: 6px !important;
        padding-right: 6px !important;
    }}

    /* =====================================================
       EXPANDER
       ===================================================== */

    [data-testid="stExpander"] {{
        border: 1px solid {BORDER} !important;
        border-radius: 12px !important;
        background: {CARD} !important;
    }}

    /* =====================================================
       RESPONSIVIDADE
       ===================================================== */

    @media (max-width: 900px) {{

        .block-container {{
            padding-left: 1rem;
            padding-right: 1rem;
        }}

        h1 {{
            font-size: 1.65rem !important;
        }}

        .custom-card-value {{
            font-size: 27px;
        }}

        .score-value {{
            font-size: 40px;
        }}

    }}

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# GOOGLE SHEETS
# =========================================================

SHEET_ID = "1bSYqD9wLkpMxTIGN6kyFh6zuVTixM384oQr8cGskYcM"
ABA = "Aplicação"


@st.cache_resource
def get_client():

    credenciais = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets.readonly"
        ]
    )

    return gspread.authorize(credenciais)


@st.cache_data(ttl=300)
def carregar_dados():

    gc = get_client()

    planilha = gc.open_by_key(SHEET_ID)
    aba_aplicacao = planilha.worksheet(ABA)

    return aba_aplicacao.get_all_values()


# =========================================================
# ATUALIZAÇÃO
# =========================================================

col_data, col_botao = st.columns([6, 1])

with col_botao:

    if st.button("↻ Atualizar"):

        st.cache_data.clear()
        st.rerun()


data_consulta = datetime.now().strftime(
    "%d/%m/%Y às %H:%M"
)

with col_data:

    st.caption(
        f"Última atualização dos dados: {data_consulta}"
    )


# =========================================================
# CARREGAMENTO
# =========================================================

dados_aplicacao = carregar_dados()


if len(dados_aplicacao) <= 3:

    st.error(
        "A aba 'Aplicação' não possui dados suficientes "
        "para carregar o dashboard."
    )

    st.stop()


# =========================================================
# ESTRUTURA DA PLANILHA
# =========================================================

COLUNAS_ESPERADAS = [
    "Colaborador",
    "Supervisão",
    "Data Monitoria",
    "Quem Aplicou Monitoria",
    "Ligação 1",
    "Ligação 2",
    "Data Lado a Lado",
    "Quem Aplicou Lado a Lado",
    "Observação Lado a Lado",
    "Data Monitoria Offline",
    "Quem Aplicou Offline",
    "Percentual Offline",
    "Observações Gerais"
]


linhas_dados = dados_aplicacao[3:]


if not all(
    len(linha) == len(COLUNAS_ESPERADAS)
    for linha in linhas_dados
):

    st.error(
        "A estrutura da aba 'Aplicação' foi alterada. "
        "Verifique se as colunas continuam na estrutura esperada."
    )

    st.stop()


monitorias_google = pd.DataFrame(
    linhas_dados,
    columns=COLUNAS_ESPERADAS
)


# =========================================================
# LIMPEZA
# =========================================================

monitorias_google = monitorias_google[
    monitorias_google["Colaborador"].notna()
    &
    (
        monitorias_google["Colaborador"]
        .astype(str)
        .str.strip()
        != ""
    )
].copy()


monitorias_google = monitorias_google.replace(
    {
        "": pd.NA,
        " ": pd.NA
    }
)


monitorias_google["Colaborador"] = (
    monitorias_google["Colaborador"]
    .astype("string")
    .str.strip()
)


monitorias_google["Supervisão"] = (
    monitorias_google["Supervisão"]
    .astype("string")
    .str.strip()
)


monitorias_google["Supervisão"] = (
    monitorias_google["Supervisão"]
    .replace(
        {
            "Júlio": "Julio"
        }
    )
)


# =========================================================
# DATAS
# =========================================================

for coluna in [
    "Data Monitoria",
    "Data Lado a Lado",
    "Data Monitoria Offline"
]:

    monitorias_google[coluna] = pd.to_datetime(
        monitorias_google[coluna],
        dayfirst=True,
        errors="coerce"
    )


# =========================================================
# DUPLICIDADES
# =========================================================

duplicados = (
    monitorias_google
    .groupby("Colaborador")
    .size()
)

duplicados = duplicados[
    duplicados > 1
]


if not duplicados.empty:

    with st.expander(
        f"⚠️ {len(duplicados)} colaborador(es) "
        "com mais de um registro"
    ):

        st.write(
            "Os registros não foram removidos automaticamente."
        )

        for nome, quantidade in duplicados.items():

            st.write(
                f"- {nome}: {quantidade} registros"
            )


# =========================================================
# FUNÇÕES DOS COLABORADORES
# =========================================================

execs = [
    "Gabriela Cardoso de Sousa",
    "Rayssa Sobral Araújo",
    "Monique de Souza Marques",
    "Felipe de Souza Carvalho",
    "João Paulo Ribeiro Rodrigues",
    "Amanda Ribeiro Carvalho",
    "Gabriela Salvi Sbardelotto",
    "Juliette Mendes Lima",
    "Isabela Cason",
    "Gabriella Farias de Melo",
    "Emanuele Maria Carvalho Silva",
    "Matheus Fernando de Oliveira Fernandes",
    "Milena Silva Monteiro",
    "Micaella Vieira de Moura",
    "Ana Carolina Silva Vilela",
    "Naiara Borcatt Porto",
    "Marine Vitória Guimarães Fortunato",
    "Lucas Scalambrini Caetano",
    "Guilherme Tarragô Mendonça da Silva",
    "Karine Kethely Soares",
    "Ermandos de Lacerda Ferreira",
    "Yasmim Francisca dos Santos",
    "Danilo Batista de Freitas Silva",
    "Isabel Albuquerque Checchia",
    "Maisa da Silva Pereira",
    "Roberta Camargo Zorzetto",
    "Matheus Marucci Hudzinski",
    "Mirella Pereira de Oliveira",
    "Giulia Rodrigues Pimentel",
    "Maria Eduarda Rodrigues Gama",
    "Hellen Salles de Freitas",
    "Luccas Nakamoto de Paula",
    "Tito de Jesus Nascimento",
    "Gustavo Bertholino Cardoso",
    "Marcelly Paiva da Silva",
    "Amanda Alves Ferreira",
    "Gabriel Bulhões Vieira",
    "Gabriely da Rocha Ferreira Silva",
    "Elissama Laís Cuscan Alves",
    "Ingrid Nunes da Cruz",
    "Stefany Miriam Marçal",
    "Raquel Lima Santos",
    "Julio César Merola",
    "Eduarda de Araujo Rodrigues",
    "Samuel Malheiro Ramos",
    "Ana Gabriela Moreno dos Santos",
    "Luciana de Campos Silva",
    "João Pedro Cardoso",
    "Gabriela Nerone Pinheiro",
    "Camila Alves Bender Azevedo",
    "Ian Monteiro Hernandez",
    "Luanna Soares dos Santos Siqueira",
    "Cassiele Chare Roberto",
    "Amanda Lima Pereira",
    "Letícia Lima Souza",
    "Lírian Rossete Nunes",
    "Hosana de Souza Soares",
    "Lorena da Silva Souza",
    "Jessica Carol Alves de Aguiar",
    "Isabella da Silva Neves",
    "Gabriel Colacino Pitoni",
    "Luana Ocsany Modonezi",
    "Yasmin da Fonseca Buffel Pantoja",
    "Sarah Andressa de Araújo Antunes",
    "Davi de Araujo Lima",
    "Henzo Silva Oliveira",
    "Lucas Rodrigues dos Santos Baltazar",
    "Sérgio Vinícius Souza Silva da Hora",
    "Sabrina Kahati Cardoso",
    "Cauã Petrella de Sousa",
    "Ana Beatriz de Queiroz",
    "Douglas de Souza Oliveira",
    "Sarah Rodrigues Silva",
    "Jefferson Amaral Silva Junior",
    "Cayo Soares De Souza",
    "Robson Souto Campos da Silva",
    "Mateus Custódio Dias da Conceição",
    "Eduarda Paes Leme Maldonado",
    "Isabella Santana Felix dos Santos",
    "Juliene Dolores Ferreira da Silva",
    "Aline Maria dos Santos",
    "Rebeca Beatriz Amaral Lopes",
    "João Victor Matias Belmiro",
    "Bianca da Silva Marchon",
    "Vanessa Lisboa de Pontes",
    "Arison Pereira da Costa",
    "Carla Maria da Silva",
    "Débora Viana Marim Rosa",
    "Bianca Santos de Oliveira",
    "Thaynara Ferreira Leite",
    "Bruna Ribeiro da Silva",
    "Camila Costa Gaspar",
    "Thiago Martins de Almeida",
    "Thayna de Jesus Santos",
    "Ana Beatriz De Oliveira Jovino",
    "Sabrina Rodrigues da Silva",
    "Emile Cristine Brito da Silva",
    "Aline Trindade Moreira",
    "Erik Xavier Gonçalves",
    "Keren Jamille Coutinho Albrechete"
]


apoio_adm = [
    "Felipe Santos Nery",
    "Pedro Llanos Iampietro",
    "Matheus Lacerda Lima",
    "Angel Almeida Braga",
    "Evellyn Silva dos Santos",
    "Felipe Félix da Rocha Lima",
    "Isabelle Steidl de Oliveira",
    "Pedro Paulo Clemente Torres",
    "Gabriel Soares Gonçalves",
    "Fernanda Dias da Silva",
    "Bruna Clementino Graça",
    "Emilly Oliveira França",
    "Laura Marques da Silva",
    "Amanda Cruz dos Santos",
    "Ana Carolina Gabriel Amador",
    "Juliana Santos de Freitas",
    "Wendy Aparecida Vieira Sabino",
    "Alessandra da Silva dos Santos",
    "Andressa Caroline Pereira Santana",
    "Ana Luiza Cavalcante Silva",
    "Lidiane Israel Domingos",
    "Nataly Freitas Souza Santos",
    "Beatriz Fusari Martins Moreira",
    "Davi Rodrigues da Silva",
    "Igor Silva Leite",
    "Amanda Ferreira da Silva",
    "Maria Clara Duarte Alves",
    "Cristina de Deus Aguiar Stoski",
    "Ana Beatriz Rodrigues Proença",
    "Amanda Brito da Silva",
    "Stella Angela da Silva"
]


funcao_por_nome = {}

for nome in execs:
    funcao_por_nome[nome] = "Exec"

for nome in apoio_adm:
    funcao_por_nome[nome] = "Apoio ADM"


monitorias_google["Função"] = (
    monitorias_google["Colaborador"]
    .map(funcao_por_nome)
    .fillna("Não identificado")
)


# =========================================================
# NOTAS
# =========================================================

notas_monitoria = {
    "Pedro Llanos Iampietro": [75.26, 76.46],
    "Matheus Lacerda Lima": [94.00, 77.66],
    "Gabriel Soares Gonçalves": [80.73, 80.66],
    "Laura Marques da Silva": [75.86, 81.93],
    "Felipe Santos Nery": [77.66, 75.86],
    "Evellyn Silva dos Santos": [86.20, 81.22],
    "Maria Eduarda Rodrigues Gama": [60.00, 63.60],
    "Isabella da Silva Neves": [50.00, 66.60],
    "Douglas de Souza Oliveira": [67.40, 62.60],
    "Keren Jamille Coutinho Albrechete": [82.60, 65.80],
    "Jessica Carol Alves de Aguiar": [51.80, 60.20],
    "Ana Beatriz de Queiroz": [57.20, 51.20],
    "Amanda Ferreira da Silva": [73.46, 72.86],
    "Eduarda Paes Leme Maldonado": [85.00, 49.20],
    "Isabella Santana Felix dos Santos": [58.80, 54.80],
    "Emanuele Maria Carvalho Silva": [61.20, 54.60],
    "Angel Almeida Braga": [65.20, 62.60],
    "Pedro Paulo Clemente Torres": [66.04, 75.50],
    "Raquel Lima Santos": [58.56, 46.64],
    "Cassiele Chare Roberto": [55.80, 56.40],
    "Lorena da Silva Souza": [71.40, 61.20],
    "Beatriz Fusari Martins Moreira": [74.60, 69.86],
    "Sabrina Rodrigues da Silva": [68.52, 66.00],
    "Sabrina Kahati Cardoso": [60.00, 68.60],
    "Guilherme Tarragô Mendonça da Silva": [63.20, 51.20],
    "Karine Kethely Soares": [67.40, 61.80],
    "Ingrid Nunes da Cruz": [67.20, 51.20],
    "Luanna Soares dos Santos Siqueira": [51.20, 52.02],
    "Sérgio Vinícius Souza Silva da Hora": [71.60, 63.86],
    "Emile Cristine Brito da Silva": [77.52, 52.63],
    "Aline Trindade Moreira": [69.60, 39.80],
    "Cauã Petrella de Sousa": [66.00, 57.52],
    "Giulia Rodrigues Pimentel": [64.80, 42.80],
    "Elissama Laís Cuscan Alves": [56.60, 65.00],
    "Ana Luiza Cavalcante Silva": [69.26, 65.00],
    "Ana Beatriz De Oliveira Jovino": [91.18, 83.40],
    "Erik Xavier Gonçalves": [77.80, 51.20],
    "Gabriella Farias de Melo": [63.00, 67.08],
    "Lucas Rodrigues dos Santos Baltazar": [56.00, 63.60],
    "Gabriely da Rocha Ferreira Silva": [57.48, 56.68],
    "Henzo Silva Oliveira": [88.00],
    "Stefany Miriam Marçal": [62.00, 41.00],
    "Lucas Scalambrini Caetano": [82.00, 65.80],
    "Juliette Mendes Lima": [58.80, 74.40],
    "Isabela Cason": [61.20, 67.60],
    "Mateus Custódio Dias da Conceição": [75.60, 69.60],
    "Gabriela Salvi Sbardelotto": [56.00, 63.00],
    "Juliana Santos de Freitas": [84.33, 76.46],
    "Davi de Araujo Lima": [60.80, 54.20],
    "Nataly Freitas Souza Santos": [73.46, 75.90],
    "Gabriel Bulhões Vieira": [52.40, 65.00],
    "Bruna Clementino Graça": [74.73, 83.80],
    "Ian Monteiro Hernandez": [57.00, 53.80],
    "Cristina de Deus Aguiar Stoski": [69.90, 95.20],
    "Ana Beatriz Rodrigues Proença": [68.66, 91.00],
    "Emilly Oliveira França": [77.06, 79.46],
    "Mirella Pereira de Oliveira": [69.98, 77.52],
    "Danilo Batista de Freitas Silva": [86.20, 74.40],
    "Amanda Ribeiro Carvalho": [70.20, 65.20],
    "Ana Carolina Gabriel Amador": [85.53, 87.40],
    "Rebeca Beatriz Amaral Lopes": [79.20, 81.00],
    "Monique de Souza Marques": [64.60, 74.40],
    "Marcelly Paiva da Silva": [66.00, 69.00],
    "Jefferson Amaral Silva Junior": [66.80, 73.00],
    "Yasmim Francisca dos Santos": [62.00, 49.40],
    "Eduarda de Araujo Rodrigues": [76.60, 58.40],
    "Rayssa Sobral Araújo": [72.00, 70.00],
    "Amanda Lima Pereira": [69.60, 71.80],
    "Gustavo Bertholino Cardoso": [82.00, 74.80],
    "Hosana de Souza Soares": [79.60, 75.40],
    "Naiara Borcatt Porto": [70.20, 73.80],
    "Matheus Marucci Hudzinski": [67.20, 70.20],
    "Letícia Lima Souza": [70.80, 64.60],
    "Robson Souto Campos da Silva": [87.40, 89.98]
}


def calcular_media_notas(nome):

    notas = notas_monitoria.get(nome, [])

    if not notas:
        return None

    return sum(notas) / len(notas)


monitorias_google["Média"] = (
    monitorias_google["Colaborador"]
    .apply(calcular_media_notas)
)


# =========================================================
# STATUS
# =========================================================

# REGRA OFICIAL:
# Data Monitoria preenchida = realizada

monitorias_google["Realizada"] = (
    monitorias_google["Data Monitoria"].notna()
)


# =========================================================
# PRAÇAS
# =========================================================

pracas = {
    "São Paulo": {
        "responsavel": "Danielly Palaro",
        "supervisores": [
            "Wesley Alves Martins",
            "Kelly Gonzaga Querido",
            "Jean Cássio Negri dos Santos",
            "Julio César Castro",
            "Aline Ramalho Pimentel",
            "Murilo Henrique Xavier"
        ]
    },

    "GMSP": {
        "responsavel": "Caio Marques",
        "supervisores": [
            "Camila Dias Silva",
            "Laila Cerqueira Rodrigues",
            "Alexssander Affonso da Silva"
        ]
    },

    "Conne-Sul": {
        "responsavel": "Evelyn Viegas",
        "supervisores": [
            "Angelica Yumi Gaspar de Oliveira",
            "Karine Conceição Rodrigues"
        ]
    },

    "Sudeste": {
        "responsavel": "Darlene Carvalho",
        "supervisores": [
            "Maiara Bravo",
            "Letícia da Silva Santos"
        ]
    }
}


# =========================================================
# MAPEAMENTO REAL:
# PRAÇA -> NOME DA SUPERVISÃO NA PLANILHA
# =========================================================

supervisao_por_praca = {

    "São Paulo": [
        "Wesley",
        "Kelly",
        "Jean",
        "Julio",
        "Murilo"
    ],

    "GMSP": [
        "Camila",
        "Laila",
        "Alexssander"
    ],

    "Conne-Sul": [
        "Angélica",
        "Karine"
    ],

    "Sudeste": [
        "Maiara",
        "Leticia"
    ]
}


# Inverte o dicionário para descobrir
# a praça a partir da supervisão

praca_por_supervisao = {}

for praca, supervisoes in supervisao_por_praca.items():

    for supervisao in supervisoes:

        praca_por_supervisao[
            supervisao
        ] = praca


monitorias_google["Praça"] = (
    monitorias_google["Supervisão"]
    .map(praca_por_supervisao)
    .fillna("Não identificada")
)


# =========================================================
# FUNÇÕES VISUAIS
# =========================================================

def html_card(
    titulo,
    valor,
    subtitulo=""
):

    titulo = html.escape(str(titulo))
    valor = html.escape(str(valor))
    subtitulo = html.escape(str(subtitulo))

    return f"""
    <div class="custom-card">

        <div class="custom-card-title">
            {titulo}
        </div>

        <div class="custom-card-value">
            {valor}
        </div>

        <div class="custom-card-subtitle">
            {subtitulo}
        </div>

    </div>
    """


def html_praca(
    nome,
    quantidade
):

    nome = html.escape(str(nome))

    return f"""
    <div class="praca-card">

        <div class="praca-name">
            {nome}
        </div>

        <div class="praca-info">
            {quantidade} supervisões
        </div>

    </div>
    """


def html_team(
    nome,
    total,
    realizadas,
    pendentes
):

    nome = html.escape(str(nome))

    percentual = (
        realizadas / total * 100
        if total > 0
        else 0
    )

    return f"""
    <div class="team-card">

        <div class="team-name">
            {nome}
        </div>

        <div class="team-number">
            {total}
        </div>

        <div class="team-label">
            colaboradores
        </div>

        <div class="team-progress">

            <div
                class="team-progress-fill"
                style="width: {percentual:.1f}%"
            ></div>

        </div>

        <div class="team-status">

            <span class="team-realizada">
                {realizadas} realizadas
            </span>

            <span class="team-pendente">
                {pendentes} pendentes
            </span>

        </div>

    </div>
    """


def html_lista(
    titulo,
    dataframe,
    mostrar_nota=True
):

    titulo = html.escape(str(titulo))

    if dataframe.empty:

        return f"""
        <div class="list-card">

            <div class="list-title">
                {titulo}
            </div>

            <div class="empty-message">
                Nenhum colaborador nesta categoria.
            </div>

        </div>
        """

    itens = ""

    for _, row in dataframe.iterrows():

        nome = html.escape(
            str(row["Colaborador"])
        )

        funcao = html.escape(
            str(row["Função"])
        )

        nota_html = ""

        media = row["Média"]

        if (
            mostrar_nota
            and pd.notna(media)
        ):

            nota_html = f"""
            <div class="list-score">
                Média: {media:.2f}%
            </div>
            """

        itens += f"""
        <div class="list-item">

            <div class="list-name">
                {nome}
            </div>

            <div class="list-function">
                {funcao}
            </div>

            {nota_html}

        </div>
        """

    return f"""
    <div class="list-card">

        <div class="list-title">
            {titulo}
        </div>

        {itens}

    </div>
    """


# =========================================================
# CABEÇALHO
# =========================================================

st.markdown(
    f"""
    <div style="
        display:flex;
        align-items:center;
        gap:10px;
        margin-bottom:7px;
    ">

        <span style="
            display:inline-flex;
            align-items:center;
            justify-content:center;
            width:29px;
            height:29px;
            border-radius:9px;
            background:{PRIMARY_SOFT};
            color:{PRIMARY};
            font-size:13px;
            font-weight:800;
        ">
            N
        </span>

        <span style="
            color:{PRIMARY};
            font-size:11px;
            font-weight:700;
            letter-spacing:.09em;
        ">
            NUBE • TREINAMENTO COMERCIAL
        </span>

    </div>
    """,
    unsafe_allow_html=True
)

st.title(
    "Dashboard de Monitorias"
)

st.markdown(
    '<div class="subtitle">'
    'Acompanhamento das aplicações de monitoria'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# FILTROS
# =========================================================

st.subheader("Filtros")


col_filtro_praca, col_filtro_supervisao, col_filtro_status = (
    st.columns(3)
)


# ---------------------------------------------------------
# PRAÇA
# ---------------------------------------------------------

opcoes_praca = [
    "Todas"
] + list(pracas.keys())


with col_filtro_praca:

    praca_selecionada = st.selectbox(
        "Praça",
        opcoes_praca
    )


# ---------------------------------------------------------
# SUPERVISÃO
# ---------------------------------------------------------

if praca_selecionada == "Todas":

    supervisoes_disponiveis = sorted(
        monitorias_google[
            "Supervisão"
        ]
        .dropna()
        .unique()
        .tolist()
    )

else:

    supervisoes_da_praca = (
        supervisao_por_praca[
            praca_selecionada
        ]
    )

    supervisoes_existentes = (
        monitorias_google[
            "Supervisão"
        ]
        .dropna()
        .unique()
        .tolist()
    )

    supervisoes_disponiveis = sorted(
        [
            supervisao
            for supervisao
            in supervisoes_da_praca
            if supervisao
            in supervisoes_existentes
        ]
    )


opcoes_supervisao = [
    "Todas"
] + supervisoes_disponiveis


with col_filtro_supervisao:

    supervisao_selecionada = st.selectbox(
        "Supervisão",
        opcoes_supervisao
    )


# ---------------------------------------------------------
# STATUS
# ---------------------------------------------------------

with col_filtro_status:

    status_selecionado = st.selectbox(
        "Status",
        [
            "Todos",
            "Realizadas",
            "Pendentes"
        ]
    )


# =========================================================
# APLICA FILTROS
# =========================================================

df_filtrado = monitorias_google.copy()


if praca_selecionada != "Todas":

    df_filtrado = df_filtrado[
        df_filtrado["Praça"]
        == praca_selecionada
    ].copy()


if supervisao_selecionada != "Todas":

    df_filtrado = df_filtrado[
        df_filtrado["Supervisão"]
        == supervisao_selecionada
    ].copy()


if status_selecionado == "Realizadas":

    df_filtrado = df_filtrado[
        df_filtrado["Realizada"]
    ].copy()


elif status_selecionado == "Pendentes":

    df_filtrado = df_filtrado[
        ~df_filtrado["Realizada"]
    ].copy()


# =========================================================
# RESUMO DO FILTRO
# =========================================================

filtros_ativos = []

if praca_selecionada != "Todas":
    filtros_ativos.append(
        f"<strong>Praça:</strong> "
        f"{html.escape(praca_selecionada)}"
    )

if supervisao_selecionada != "Todas":
    filtros_ativos.append(
        f"<strong>Supervisão:</strong> "
        f"{html.escape(supervisao_selecionada)}"
    )

if status_selecionado != "Todos":
    filtros_ativos.append(
        f"<strong>Status:</strong> "
        f"{html.escape(status_selecionado)}"
    )


if filtros_ativos:

    st.markdown(
        '<div class="filter-summary">'
        + " &nbsp; • &nbsp; ".join(filtros_ativos)
        + "</div>",
        unsafe_allow_html=True
    )


# =========================================================
# DESEMPENHO GERAL
# =========================================================

st.subheader("Desempenho geral")

st.markdown(
    '<div class="section-caption">'
    'Média das notas das monitorias'
    '</div>',
    unsafe_allow_html=True
)


col_grafico, col_score = st.columns(
    [1, 1]
)


notas_validas = (
    df_filtrado[
        df_filtrado["Média"].notna()
    ]["Média"]
)


if len(notas_validas) > 0:

    media_geral = notas_validas.mean()

else:

    media_geral = None


with col_grafico:

    if media_geral is not None:

        restante = max(
            0,
            100 - media_geral
        )

        fig = go.Figure(
            go.Pie(
                values=[
                    media_geral,
                    restante
                ],
                labels=[
                    "Média",
                    "Restante"
                ],
                hole=0.76,
                marker=dict(
                    colors=[
                        PRIMARY,
                        "#E8EBF3"
                    ],
                    line=dict(
                        color="#FFFFFF",
                        width=3
                    )
                ),
                textinfo="none",
                hoverinfo="skip"
            )
        )

        fig.update_layout(
            showlegend=False,
            margin=dict(
                l=10,
                r=10,
                t=10,
                b=10
            ),
            height=250,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(
                family="Inter, sans-serif",
                color=TEXT
            ),
            annotations=[
                dict(
                    text=f"<b>{media_geral:.1f}%</b>",
                    x=0.5,
                    y=0.5,
                    font=dict(
                        size=28,
                        color=TEXT,
                        family="Inter, sans-serif"
                    ),
                    showarrow=False
                )
            ]
        )

    else:

        fig = go.Figure()

        fig.update_layout(
            showlegend=False,
            margin=dict(
                l=10,
                r=10,
                t=10,
                b=10
            ),
            height=250,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(
                family="Inter, sans-serif",
                color=TEXT
            ),
            annotations=[
                dict(
                    text="<b>—</b>",
                    x=0.5,
                    y=0.5,
                    font=dict(
                        size=34,
                        color=TEXT
                    ),
                    showarrow=False
                )
            ]
        )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False
        }
    )


with col_score:

    quantidade_com_nota = (
        df_filtrado[
            df_filtrado["Média"].notna()
        ].shape[0]
    )

    st.html(
        f"""
        <div class="score-card">

            <div class="score-label">
                COLABORADORES COM NOTA REGISTRADA
            </div>

            <div class="score-value">
                {quantidade_com_nota}
            </div>

            <div class="score-description">
                Média calculada a partir das notas
                disponíveis nas monitorias.
            </div>

        </div>
        """
    )


# =========================================================
# RESUMO
# =========================================================

st.subheader("Resumo")


total_colaboradores = len(
    df_filtrado
)


total_realizadas = int(
    df_filtrado["Realizada"].sum()
)


total_pendentes = (
    total_colaboradores
    - total_realizadas
)


percentual_concluido = (
    total_realizadas
    / total_colaboradores
    * 100
    if total_colaboradores > 0
    else 0
)


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.html(
        html_card(
            "COLABORADORES",
            total_colaboradores,
            "no acompanhamento"
        )
    )


with col2:

    st.html(
        html_card(
            "REALIZADAS",
            total_realizadas,
            "monitorias concluídas"
        )
    )


with col3:

    st.html(
        html_card(
            "PENDENTES",
            total_pendentes,
            "monitorias a realizar"
        )
    )


with col4:

    st.html(
        html_card(
            "% CONCLUÍDO",
            f"{percentual_concluido:.1f}%",
            "do total"
        )
    )


# =========================================================
# PRAÇAS
# =========================================================

st.subheader("Praças e equipes")


colunas_pracas = st.columns(4)


for coluna, (
    nome_praca,
    dados_praca
) in zip(
    colunas_pracas,
    pracas.items()
):

    with coluna:

        quantidade_supervisoes = len(
            supervisao_por_praca[
                nome_praca
            ]
        )

        st.html(
            html_praca(
                nome_praca,
                quantidade_supervisoes
            )
        )


# =========================================================
# ACOMPANHAMENTO POR EQUIPE
# =========================================================

st.subheader(
    "Acompanhamento por equipe"
)


if supervisao_selecionada == "Todas":

    nomes_supervisoes = sorted(
        df_filtrado[
            "Supervisão"
        ]
        .dropna()
        .unique()
        .tolist()
    )


    if not nomes_supervisoes:

        st.html(
            """
            <div class="list-card">

                <div class="empty-message">
                    Nenhuma equipe encontrada
                    para os filtros selecionados.
                </div>

            </div>
            """
        )


    for inicio in range(
        0,
        len(nomes_supervisoes),
        4
    ):

        grupo = nomes_supervisoes[
            inicio:inicio + 4
        ]


        colunas = st.columns(4)


        for coluna, supervisao in zip(
            colunas,
            grupo
        ):

            df_supervisao = (
                df_filtrado[
                    df_filtrado["Supervisão"]
                    == supervisao
                ]
            )


            total = len(
                df_supervisao
            )


            realizadas = int(
                df_supervisao[
                    "Realizada"
                ].sum()
            )


            pendentes = (
                total
                - realizadas
            )


            with coluna:

                st.html(
                    html_team(
                        supervisao,
                        total,
                        realizadas,
                        pendentes
                    )
                )


else:

    df_supervisao = (
        df_filtrado[
            df_filtrado["Supervisão"]
            == supervisao_selecionada
        ].copy()
    )


    if status_selecionado == "Realizadas":

        realizadas_df = (
            df_supervisao[
                df_supervisao["Realizada"]
            ].copy()
        )

        pendentes_df = pd.DataFrame(
            columns=df_supervisao.columns
        )


    elif status_selecionado == "Pendentes":

        realizadas_df = pd.DataFrame(
            columns=df_supervisao.columns
        )

        pendentes_df = (
            df_supervisao[
                ~df_supervisao["Realizada"]
            ].copy()
        )


    else:

        realizadas_df = (
            df_supervisao[
                df_supervisao["Realizada"]
            ].copy()
        )

        pendentes_df = (
            df_supervisao[
                ~df_supervisao["Realizada"]
            ].copy()
        )


    col_realizadas, col_pendentes = (
        st.columns(2)
    )


    with col_realizadas:

        st.html(
            html_lista(
                f"Realizadas · "
                f"{len(realizadas_df)}",
                realizadas_df,
                mostrar_nota=True
            )
        )


    with col_pendentes:

        st.html(
            html_lista(
                f"Pendentes · "
                f"{len(pendentes_df)}",
                pendentes_df,
                mostrar_nota=False
            )
        )


# =========================================================
# PENDÊNCIAS
# =========================================================

st.subheader("Pendências")


pendencias = df_filtrado[
    ~df_filtrado["Realizada"]
].copy()


pendencias = pendencias.sort_values(
    by=[
        "Supervisão",
        "Colaborador"
    ],
    na_position="last"
)


if pendencias.empty:

    st.html(
        """
        <div class="list-card">

            <div class="list-title">
                Nenhuma pendência
            </div>

            <div class="empty-message">
                Não há colaboradores pendentes
                nos filtros selecionados.
            </div>

        </div>
        """
    )


else:

    col_pend_1, col_pend_2 = (
        st.columns(2)
    )


    metade = (
        len(pendencias) + 1
    ) // 2


    pendencias_1 = (
        pendencias.iloc[:metade]
    )

    pendencias_2 = (
        pendencias.iloc[metade:]
    )


    with col_pend_1:

        st.html(
            html_lista(
                f"Colaboradores pendentes · "
                f"{len(pendencias)}",
                pendencias_1,
                mostrar_nota=False
            )
        )


    with col_pend_2:

        st.html(
            html_lista(
                "",
                pendencias_2,
                mostrar_nota=False
            )
        )


# =========================================================
# EVOLUÇÃO
# =========================================================

st.subheader(
    "Evolução das Monitorias"
)


datas_validas = (
    df_filtrado[
        df_filtrado["Data Monitoria"].notna()
    ]["Data Monitoria"]
)


if not datas_validas.empty:

    primeiro_mes = (
        datas_validas
        .min()
        .to_period("M")
    )

    ultimo_mes = max(
        datas_validas
        .max()
        .to_period("M"),
        pd.Timestamp.today()
        .to_period("M")
    )

    meses = pd.period_range(
        primeiro_mes,
        ultimo_mes,
        freq="M"
    )

else:

    meses = pd.period_range(
        pd.Timestamp.today()
        .to_period("M"),
        pd.Timestamp.today()
        .to_period("M"),
        freq="M"
    )


quantidades = []
nomes_meses = []


for periodo in meses:

    inicio_mes = (
        periodo.start_time
    )

    fim_mes = (
        periodo.end_time
    )


    quantidade = (
        df_filtrado[
            (
                df_filtrado[
                    "Data Monitoria"
                ] >= inicio_mes
            )
            &
            (
                df_filtrado[
                    "Data Monitoria"
                ] <= fim_mes
            )
        ]
        .shape[0]
    )


    quantidades.append(
        quantidade
    )


    nomes_meses.append(
        periodo
        .strftime("%b/%y")
        .capitalize()
    )


fig_evolucao = go.Figure()


fig_evolucao.add_trace(
    go.Bar(
        x=nomes_meses,
        y=quantidades,
        marker=dict(
            color=PRIMARY,
            line=dict(
                width=0
            )
        ),
        text=quantidades,
        textposition="outside",
        textfont=dict(
            color=TEXT,
            size=11
        ),
        hovertemplate=(
            "%{x}: %{y} monitorias"
            "<extra></extra>"
        )
    )
)


fig_evolucao.update_layout(
    height=360,
    margin=dict(
        l=10,
        r=10,
        t=25,
        b=10
    ),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(
        family="Inter, sans-serif",
        color=TEXT
    ),
    xaxis=dict(
        title=None,
        showgrid=False,
        linecolor=BORDER,
        tickfont=dict(
            size=11,
            color=SECONDARY
        )
    ),
    yaxis=dict(
        title=None,
        showgrid=True,
        gridcolor="#EDF0F5",
        zeroline=False,
        tickfont=dict(
            size=11,
            color=SECONDARY
        )
    ),
    bargap=0.32,
    showlegend=False
)


st.plotly_chart(
    fig_evolucao,
    use_container_width=True,
    config={
        "displayModeBar": False
    }
)


# =========================================================
# OUTRAS ETAPAS
# =========================================================

st.subheader(
    "Outras etapas"
)


col_lado, col_offline = (
    st.columns(2)
)


total_lado_a_lado = int(
    df_filtrado[
        "Data Lado a Lado"
    ].notna().sum()
)


total_offline = int(
    df_filtrado[
        "Data Monitoria Offline"
    ].notna().sum()
)


with col_lado:

    status_lado = (
        f"{total_lado_a_lado} realizados"
        if total_lado_a_lado > 0
        else "Ainda não iniciado"
    )


    st.html(
        f"""
        <div class="custom-card">

            <div class="custom-card-title">
                LADO A LADO
            </div>

            <div class="custom-card-value">
                {total_lado_a_lado}
            </div>

            <div class="custom-card-subtitle">
                {status_lado}
            </div>

        </div>
        """
    )


with col_offline:

    status_offline = (
        f"{total_offline} realizados"
        if total_offline > 0
        else "Ainda não iniciado"
    )


    st.html(
        f"""
        <div class="custom-card">

            <div class="custom-card-title">
                MONITORIA OFFLINE
            </div>

            <div class="custom-card-value">
                {total_offline}
            </div>

            <div class="custom-card-subtitle">
                {status_offline}
            </div>

        </div>
        """
    )
