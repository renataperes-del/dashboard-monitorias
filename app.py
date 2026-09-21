import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import gspread
import html
import unicodedata

from datetime import datetime
from zoneinfo import ZoneInfo
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

    @import url(
        'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
    );

    .stApp,
    .stApp p,
    .stApp label,
    .stApp button,
    .stApp input,
    .stApp h1,
    .stApp h2,
    .stApp h3,
    .stApp li {{
        font-family: 'Inter', sans-serif;
    }}

    .stApp {{
        background: {BG};
        color: {TEXT};
    }}

    .block-container {{
        max-width: 1400px;
        padding-top: 1.5rem;
        padding-bottom: 4rem;
    }}

    #MainMenu,
    footer {{
        visibility: hidden;
    }}

    [data-testid="stHeader"] {{
        background: transparent !important;
    }}

    h1 {{
        color: {TEXT} !important;
        font-size: 2rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.04em;
        margin-bottom: 3px !important;
    }}

    h2,
    h3 {{
        color: {TEXT} !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }}

    h2 {{
        font-size: 1.2rem !important;
        margin-top: 30px !important;
    }}

    h3 {{
        font-size: 1rem !important;
    }}

    p {{
        color: {TEXT};
    }}

    .section-caption {{
        color: {SECONDARY};
        font-size: 13px;
        margin-top: -8px;
        margin-bottom: 16px;
    }}


    /* =====================================================
       SELECTBOX
       ===================================================== */

    div[data-baseweb="select"] > div {{
        background: {CARD};
        border: 1px solid {BORDER};
        border-radius: 12px;
        min-height: 44px;
        box-shadow: none;
        transition: all .15s ease;
    }}

    div[data-baseweb="select"] > div:hover {{
        border-color: {PRIMARY};
        box-shadow: 0 0 0 3px {PRIMARY_SOFT};
    }}


    /* =====================================================
       BOTÕES
       ===================================================== */

    .stButton > button {{
        background: {CARD};
        color: {TEXT};
        border: 1px solid {BORDER};
        border-radius: 12px;
        min-height: 44px;
        font-weight: 600;
        box-shadow: none;
        transition: all .15s ease;
    }}

    .stButton > button:hover {{
        border-color: {PRIMARY};
        color: {PRIMARY};
        background: {PRIMARY_SOFT};
    }}


    /* =====================================================
       CARDS
       ===================================================== */

    .custom-card {{
        background: {CARD};
        border: 1px solid {BORDER};
        border-radius: 16px;
        padding: 21px;
        min-height: 126px;
        box-shadow: 0 3px 12px rgba(31, 41, 55, .035);
        transition: all .15s ease;
    }}

    .custom-card:hover {{
        border-color: #D8DEEF;
        box-shadow: 0 7px 20px rgba(31, 41, 55, .055);
        transform: translateY(-1px);
    }}

    .custom-card-title {{
        color: {SECONDARY};
        font-size: 12px;
        font-weight: 700;
        letter-spacing: .07em;
        margin-bottom: 12px;
    }}

    .custom-card-value {{
        color: {TEXT};
        font-size: 30px;
        font-weight: 800;
        line-height: 1;
        font-variant-numeric: tabular-nums;
    }}

    .custom-card-subtitle {{
        color: {SECONDARY};
        font-size: 12px;
        margin-top: 9px;
    }}


    /* =====================================================
       CABEÇALHO
       ===================================================== */

    .dashboard-brand {{
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 10px;
    }}

    .brand-icon {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        border-radius: 10px;
        background: {PRIMARY_SOFT};
        color: {PRIMARY};
        font-size: 14px;
        font-weight: 800;
    }}

    .brand-text {{
        color: {PRIMARY};
        font-size: 11px;
        font-weight: 700;
        letter-spacing: .09em;
    }}

    .dashboard-header {{
        background: linear-gradient(
            135deg,
            #FFFFFF 0%,
            #F9FAFF 100%
        );
        border: 1px solid {BORDER};
        border-radius: 18px;
        padding: 24px 26px;
        margin-bottom: 20px;
        box-shadow: 0 4px 18px rgba(31, 41, 55, .035);
    }}


    /* =====================================================
       PRAÇAS
       ===================================================== */

    .praca-card {{
        background: {CARD};
        border: 1px solid {BORDER};
        border-radius: 16px;
        padding: 20px;
        min-height: 135px;
        box-shadow: 0 3px 12px rgba(31, 41, 55, .035);
        transition: all .15s ease;
    }}

    .praca-card:hover {{
        border-color: #D8DEEF;
        transform: translateY(-1px);
        box-shadow: 0 7px 20px rgba(31, 41, 55, .055);
    }}

    .praca-name {{
        color: {TEXT};
        font-size: 19px;
        font-weight: 800;
        margin-bottom: 9px;
        letter-spacing: -.025em;
    }}

    .praca-info {{
        color: {SECONDARY};
        font-size: 12px;
        line-height: 1.55;
    }}

    .praca-dot {{
        display: inline-block;
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: {PRIMARY};
        margin-right: 6px;
    }}


    /* =====================================================
       SCORE
       ===================================================== */

    .score-card {{
        background: {CARD};
        border: 1px solid {BORDER};
        border-radius: 16px;
        padding: 28px;
        min-height: 250px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 0 3px 12px rgba(31, 41, 55, .035);
    }}

    .score-label {{
        color: {SECONDARY};
        font-size: 12px;
        font-weight: 700;
        letter-spacing: .07em;
        margin-bottom: 12px;
    }}

    .score-value {{
        color: {TEXT};
        font-size: 42px;
        font-weight: 800;
        line-height: 1;
        font-variant-numeric: tabular-nums;
    }}

    .score-description {{
        color: {SECONDARY};
        font-size: 12px;
        margin-top: 12px;
        line-height: 1.5;
    }}


    /* =====================================================
       EQUIPE
       ===================================================== */

    .team-card {{
        background: {CARD};
        border: 1px solid {BORDER};
        border-radius: 16px;
        padding: 20px;
        min-height: 174px;
        box-shadow: 0 3px 12px rgba(31, 41, 55, .035);
        transition: all .15s ease;
    }}

    .team-card:hover {{
        border-color: #D8DEEF;
        transform: translateY(-1px);
        box-shadow: 0 7px 20px rgba(31, 41, 55, .055);
    }}

    .team-name {{
        color: {TEXT};
        font-size: 15px;
        font-weight: 700;
        margin-bottom: 14px;
    }}

    .team-number {{
        color: {TEXT};
        font-size: 28px;
        font-weight: 800;
        line-height: 1;
        font-variant-numeric: tabular-nums;
    }}

    .team-label {{
        color: {SECONDARY};
        font-size: 12px;
        margin-top: 4px;
    }}

    .team-progress {{
        width: 100%;
        height: 7px;
        background: #EEF1F6;
        border-radius: 99px;
        margin-top: 17px;
        overflow: hidden;
    }}

    .team-progress-fill {{
        height: 100%;
        background: linear-gradient(
            90deg,
            {PRIMARY},
            #6680F2
        );
        border-radius: 99px;
    }}

    .team-status {{
        display: flex;
        justify-content: space-between;
        margin-top: 9px;
        font-size: 12px;
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
        padding: 20px;
        min-height: 160px;
        box-shadow: 0 3px 12px rgba(31, 41, 55, .035);
    }}

    .list-title {{
        color: {TEXT};
        font-size: 15px;
        font-weight: 700;
        margin-bottom: 14px;
    }}

    .list-item {{
        border-bottom: 1px solid {BORDER};
        padding: 10px 0;
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
        font-size: 12px;
        margin-top: 3px;
    }}

    .list-score {{
        color: {PRIMARY};
        font-size: 12px;
        font-weight: 700;
        margin-top: 4px;
        font-variant-numeric: tabular-nums;
    }}

    .empty-message {{
        color: {SECONDARY};
        font-size: 12px;
        padding: 12px 0;
    }}


    /* =====================================================
       FILTRO ATIVO
       ===================================================== */

    .filter-summary {{
        background: {PRIMARY_SOFT};
        border: 1px solid #DCE4FF;
        border-radius: 12px;
        padding: 12px 16px;
        margin-top: 8px;
        margin-bottom: 24px;
        color: {TEXT};
        font-size: 12px;
    }}

    .filter-summary strong {{
        color: {PRIMARY};
    }}


    /* =====================================================
       AVISOS
       ===================================================== */

    .data-warning {{
        background: {WARNING_SOFT};
        border: 1px solid #F6D7A7;
        border-radius: 12px;
        padding: 12px 16px;
        color: {TEXT};
        font-size: 12px;
        margin-bottom: 18px;
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

    try:

        gc = get_client()

        planilha = gc.open_by_key(SHEET_ID)
        aba_aplicacao = planilha.worksheet(ABA)

        valores = aba_aplicacao.get_all_values()

        horario_atualizacao = datetime.now(
            ZoneInfo("America/Sao_Paulo")
        ).strftime("%d/%m/%Y às %H:%M")

        return valores, horario_atualizacao

    except Exception as erro:

        raise RuntimeError(
            "Não foi possível carregar os dados da planilha. "
            "Verifique a conexão com o Google Sheets, as permissões "
            "da conta de serviço ou tente atualizar novamente."
        ) from erro


# =========================================================
# ATUALIZAÇÃO
# =========================================================

col_data, col_botao = st.columns([6, 1])

with col_botao:

    if st.button("↻ Atualizar"):

        st.cache_data.clear()
        st.rerun()


# =========================================================
# CARREGAMENTO
# =========================================================

try:

    dados_aplicacao, data_consulta = carregar_dados()

except RuntimeError as erro:

    st.error(str(erro))
    st.stop()


with col_data:

    st.caption(
        f"Última atualização dos dados: {data_consulta}"
    )


# =========================================================
# VALIDAÇÃO INICIAL
# =========================================================

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


linhas_dados = []

for linha in dados_aplicacao[3:]:

    if len(linha) < len(COLUNAS_ESPERADAS):
        linha = linha + (
            [""] *
            (len(COLUNAS_ESPERADAS) - len(linha))
        )

    linhas_dados.append(
        linha[:len(COLUNAS_ESPERADAS)]
    )


if not linhas_dados:

    st.error(
        "Não foram encontradas linhas de colaboradores "
        "na aba 'Aplicação'."
    )

    st.stop()


monitorias_google = pd.DataFrame(
    linhas_dados,
    columns=COLUNAS_ESPERADAS
)


# =========================================================
# FUNÇÃO DE NORMALIZAÇÃO
# =========================================================

def normalizar_texto(valor):

    if pd.isna(valor):
        return ""

    texto = str(valor).strip()

    texto = " ".join(
        texto.split()
    )

    texto = unicodedata.normalize(
        "NFKD",
        texto
    )

    texto = "".join(
        caractere
        for caractere in texto
        if not unicodedata.combining(caractere)
    )

    return texto.casefold()


def primeiro_nome(valor):

    texto = normalizar_texto(valor)

    if not texto:
        return ""

    return texto.split()[0]


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


# =========================================================
# DATAS
# =========================================================

COLUNAS_DATA = [
    "Data Monitoria",
    "Data Lado a Lado",
    "Data Monitoria Offline"
]


datas_invalidas = {}


for coluna in COLUNAS_DATA:

    texto_original = (
        monitorias_google[coluna]
        .astype("string")
        .str.strip()
    )

    preenchidas = (
        texto_original.notna()
        &
        (texto_original != "")
    )

    convertida = pd.to_datetime(
        texto_original,
        format="%d/%m/%Y",
        errors="coerce"
    )

    falhas = (
        preenchidas
        &
        convertida.isna()
    )

    if falhas.any():

        datas_invalidas[coluna] = (
            monitorias_google.loc[
                falhas,
                "Colaborador"
            ]
            .astype(str)
            .tolist()
        )

    monitorias_google[coluna] = convertida


if datas_invalidas:

    quantidade_datas_invalidas = sum(
        len(nomes)
        for nomes in datas_invalidas.values()
    )

    st.warning(
        f"⚠️ Foram encontradas {quantidade_datas_invalidas} "
        "data(s) fora do formato esperado (dd/mm/aaaa). "
        "Essas datas não foram consideradas como monitorias realizadas."
    )

    with st.expander("Ver colaboradores com data inválida"):

        for coluna, nomes in datas_invalidas.items():

            st.markdown(
                f"**{coluna}:**"
            )

            for nome in nomes:

                st.write(
                    f"- {nome}"
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


funcao_por_nome_normalizada = {}

for nome in execs:

    funcao_por_nome_normalizada[
        normalizar_texto(nome)
    ] = "Exec"


for nome in apoio_adm:

    funcao_por_nome_normalizada[
        normalizar_texto(nome)
    ] = "Apoio ADM"


monitorias_google["Nome Normalizado"] = (
    monitorias_google["Colaborador"]
    .apply(normalizar_texto)
)


monitorias_google["Função"] = (
    monitorias_google["Nome Normalizado"]
    .map(funcao_por_nome_normalizada)
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


notas_monitoria_normalizadas = {
    normalizar_texto(nome): notas
    for nome, notas in notas_monitoria.items()
}


def calcular_media_notas(nome):

    notas = notas_monitoria_normalizadas.get(
        normalizar_texto(nome),
        []
    )

    if not notas:
        return None

    return sum(notas) / len(notas)


monitorias_google["Média"] = (
    monitorias_google["Colaborador"]
    .apply(calcular_media_notas)
)


# =========================================================
# STATUS OFICIAL
# =========================================================

monitorias_google["Realizada"] = (
    monitorias_google["Data Monitoria"].notna()
)


# =========================================================
# PRAÇAS
# =========================================================

# Aline Ramalho Pimentel NÃO entra aqui porque
# a equipe dela não faz parte das monitorias acompanhadas.

pracas = {

    "São Paulo": {
        "responsavel": "Danielly Palaro",
        "supervisores": [
            "Wesley Alves Martins",
            "Kelly Gonzaga Querido",
            "Jean Cássio Negri dos Santos",
            "Julio César Castro",
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
# MAPEAMENTO PRAÇA -> SUPERVISÃO
# =========================================================

praca_por_primeiro_nome_supervisao = {}


for nome_praca, dados_praca in pracas.items():

    for supervisor in dados_praca["supervisores"]:

        primeiro = primeiro_nome(
            supervisor
        )

        praca_por_primeiro_nome_supervisao[
            primeiro
        ] = nome_praca


def identificar_praca(supervisao):

    primeiro = primeiro_nome(
        supervisao
    )

    return (
        praca_por_primeiro_nome_supervisao
        .get(primeiro)
    )


monitorias_google["Praça"] = (
    monitorias_google["Supervisão"]
    .apply(identificar_praca)
)


# =========================================================
# VALIDAÇÃO DE SUPERVISÕES
# =========================================================

supervisoes_planilha = set(
    monitorias_google["Supervisão"]
    .dropna()
    .astype(str)
    .map(normalizar_texto)
    .unique()
)


supervisoes_mapeadas = set(
    praca_por_primeiro_nome_supervisao.keys()
)


supervisoes_nao_mapeadas = sorted(
    [
        supervisao
        for supervisao in (
            monitorias_google["Supervisão"]
            .dropna()
            .astype(str)
            .unique()
        )
        if primeiro_nome(supervisao)
        not in supervisoes_mapeadas
    ]
)


if supervisoes_nao_mapeadas:

    st.warning(
        "⚠️ Há supervisão(ões) na planilha que não estão "
        "mapeadas para uma praça: "
        + ", ".join(supervisoes_nao_mapeadas)
    )


# =========================================================
# FUNÇÕES VISUAIS
# =========================================================

def html_card(titulo, valor, subtitulo=""):

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


def html_praca(nome, quantidade, responsavel):

    nome = html.escape(str(nome))
    responsavel = html.escape(str(responsavel))

    return f"""
    <div class="praca-card">

        <div class="praca-name">
            <span class="praca-dot"></span>{nome}
        </div>

        <div class="praca-info">
            {quantidade} supervisões
            <br>
            Responsável: {responsavel}
        </div>

    </div>
    """


def html_team(nome, total, realizadas, pendentes):

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


def html_lista(titulo, dataframe, mostrar_nota=True):

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

        if mostrar_nota and pd.notna(media):

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

st.html(
    f"""
    <div class="dashboard-header">

        <div class="dashboard-brand">

            <span class="brand-icon">
                N
            </span>

            <span class="brand-text">
                NUBE • TREINAMENTO COMERCIAL
            </span>

        </div>

        <div style="
            color:{TEXT};
            font-size:32px;
            font-weight:800;
            letter-spacing:-.04em;
            line-height:1.1;
            margin-top:8px;
        ">
            Dashboard de Monitorias
        </div>

        <div style="
            color:{SECONDARY};
            font-size:14px;
            margin-top:8px;
        ">
            Acompanhamento das aplicações de monitoria
        </div>

    </div>
    """
)


# =========================================================
# FILTROS
# =========================================================

st.subheader("Filtros")


col_filtro_praca, col_filtro_supervisao, col_filtro_status = (
    st.columns(3)
)


opcoes_praca = [
    "Todas"
] + list(pracas.keys())


with col_filtro_praca:

    praca_selecionada = st.selectbox(
        "Praça",
        opcoes_praca
    )


if praca_selecionada == "Todas":

    supervisoes_disponiveis = sorted(
        monitorias_google[
            "Supervisão"
        ]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

else:

    supervisoes_da_praca = [
        primeiro_nome(nome)
        for nome in pracas[
            praca_selecionada
        ]["supervisores"]
    ]

    supervisoes_disponiveis = sorted(
        [
            supervisao
            for supervisao in (
                monitorias_google[
                    "Supervisão"
                ]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )
            if primeiro_nome(supervisao)
            in supervisoes_da_praca
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
# FILTROS PRINCIPAIS
# STATUS NÃO ENTRA AQUI
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
        .astype(str)
        .map(primeiro_nome)
        ==
        primeiro_nome(
            supervisao_selecionada
        )
    ].copy()


# =========================================================
# LISTA COM FILTRO DE STATUS
# =========================================================

if status_selecionado == "Realizadas":

    df_lista = df_filtrado[
        df_filtrado["Realizada"]
    ].copy()

elif status_selecionado == "Pendentes":

    df_lista = df_filtrado[
        ~df_filtrado["Realizada"]
    ].copy()

else:

    df_lista = df_filtrado.copy()


# =========================================================
# RESUMO DOS FILTROS
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
        f"<strong>Status das listas:</strong> "
        f"{html.escape(status_selecionado)}"
    )


if filtros_ativos:

    st.html(
        '<div class="filter-summary">'
        + " &nbsp; • &nbsp; ".join(filtros_ativos)
        + "</div>"
    )


# =========================================================
# DESEMPENHO GERAL
# USA df_filtrado, NÃO df_lista
# =========================================================

st.subheader("Desempenho geral")


st.markdown(
    '<div class="section-caption">'
    'Média das notas das monitorias'
    '</div>',
    unsafe_allow_html=True
)


col_grafico, col_score = st.columns([1, 1])


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
                        "#E9EDF5"
                    ]
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
            annotations=[
                dict(
                    text=f"<b>{media_geral:.1f}%</b>",
                    x=0.5,
                    y=0.5,
                    font=dict(
                        size=27,
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
# USA df_filtrado, NÃO df_lista
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
            dados_praca["supervisores"]
        )

        st.html(
            html_praca(
                nome_praca,
                quantidade_supervisoes,
                dados_praca["responsavel"]
            )
        )


# =========================================================
# ACOMPANHAMENTO POR EQUIPE
# USA df_filtrado
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
        .astype(str)
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
            .astype(str)
            .map(normalizar_texto)
            ==
            normalizar_texto(
                supervisao_selecionada
            )
        ].copy()
    )


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


    total_supervisao = len(
        df_supervisao
    )


    total_realizadas_supervisao = int(
        df_supervisao["Realizada"].sum()
    )


    total_pendentes_supervisao = (
        total_supervisao
        - total_realizadas_supervisao
    )


    col_team, col_info = st.columns([1, 2])


    with col_team:

        st.html(
            html_team(
                supervisao_selecionada,
                total_supervisao,
                total_realizadas_supervisao,
                total_pendentes_supervisao
            )
        )


    with col_info:

        if status_selecionado == "Realizadas":

            st.html(
                html_lista(
                    f"Realizadas · {len(realizadas_df)}",
                    realizadas_df,
                    mostrar_nota=True
                )
            )

        elif status_selecionado == "Pendentes":

            st.html(
                html_lista(
                    f"Pendentes · {len(pendentes_df)}",
                    pendentes_df,
                    mostrar_nota=False
                )
            )

        else:

            col_realizadas, col_pendentes = (
                st.columns(2)
            )

            with col_realizadas:

                st.html(
                    html_lista(
                        f"Realizadas · {len(realizadas_df)}",
                        realizadas_df,
                        mostrar_nota=True
                    )
                )

            with col_pendentes:

                st.html(
                    html_lista(
                        f"Pendentes · {len(pendentes_df)}",
                        pendentes_df,
                        mostrar_nota=False
                    )
                )


# =========================================================
# PENDÊNCIAS
# LISTA ÚNICA + DOWNLOAD
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

    st.html(
        html_lista(
            f"Colaboradores pendentes · {len(pendencias)}",
            pendencias,
            mostrar_nota=False
        )
    )


    pendencias_csv = pendencias[
        [
            "Colaborador",
            "Função",
            "Supervisão",
            "Praça"
        ]
    ].copy()


    pendencias_csv = pendencias_csv.rename(
        columns={
            "Colaborador": "Colaborador",
            "Função": "Função",
            "Supervisão": "Supervisão",
            "Praça": "Praça"
        }
    )


    csv = pendencias_csv.to_csv(
        index=False,
        encoding="utf-8-sig"
    )


    st.download_button(
        label="Baixar pendências em CSV",
        data=csv,
        file_name="pendencias_monitorias.csv",
        mime="text/csv"
    )


# =========================================================
# EVOLUÇÃO
# USA df_filtrado, NÃO df_lista
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
        pd.Timestamp.now()
        .to_period("M")
    )

    meses = pd.period_range(
        primeiro_mes,
        ultimo_mes,
        freq="M"
    )

else:

    meses = pd.period_range(
        pd.Timestamp.now()
        .to_period("M"),
        pd.Timestamp.now()
        .to_period("M"),
        freq="M"
    )


MESES = [
    "Jan",
    "Fev",
    "Mar",
    "Abr",
    "Mai",
    "Jun",
    "Jul",
    "Ago",
    "Set",
    "Out",
    "Nov",
    "Dez"
]


quantidades = []
nomes_meses = []


for periodo in meses:

    inicio_mes = periodo.start_time
    fim_mes = periodo.end_time

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
        f"{MESES[periodo.month - 1]}/"
        f"{str(periodo.year)[2:]}"
    )


fig_evolucao = go.Figure()


fig_evolucao.add_trace(
    go.Bar(
        x=nomes_meses,
        y=quantidades,
        marker_color=PRIMARY,
        text=quantidades,
        textposition="outside",
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
        showgrid=False
    ),
    yaxis=dict(
        title=None,
        showgrid=True,
        gridcolor=BORDER,
        zeroline=False
    ),
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
# USA df_filtrado
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
