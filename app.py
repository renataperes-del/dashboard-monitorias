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
# CORES
# =========================================================

BG = "#F7F8FC"
CARD = "#FFFFFF"
BORDER = "#E8EAF2"
TEXT = "#293241"
SECONDARY = "#7B8496"

BLUE = "#5B7CFA"
PURPLE = "#8B7CF6"
GREEN = "#55B99D"
ORANGE = "#F2A66F"
PINK = "#E58FA3"


# =========================================================
# CSS
# =========================================================

st.markdown(
    f"""
    <style>

    .stApp {{
        background: {BG};
    }}

    .block-container {{
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }}

    [data-testid="stHeader"] {{
        background: transparent !important;
    }}

    [data-testid="stToolbar"] {{
        right: 1rem;
    }}

    h1, h2, h3, h4 {{
        color: {TEXT} !important;
    }}

    .stCaption {{
        color: {SECONDARY} !important;
    }}

    div[data-baseweb="select"] > div {{
        background: {CARD};
        border: 1px solid {BORDER};
        border-radius: 12px;
    }}

    .custom-card {{
        background: {CARD};
        border: 1px solid {BORDER};
        border-radius: 18px;
        padding: 22px;
        min-height: 128px;
        box-shadow: 0 4px 14px rgba(41, 50, 65, 0.04);
    }}

    .custom-card-title {{
        color: {SECONDARY};
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 10px;
    }}

    .custom-card-value {{
        color: {TEXT};
        font-size: 30px;
        font-weight: 750;
        line-height: 1;
    }}

    .custom-card-subtitle {{
        color: {SECONDARY};
        font-size: 13px;
        margin-top: 8px;
    }}

    .praca-card {{
        background: {CARD};
        border: 1px solid {BORDER};
        border-radius: 18px;
        padding: 24px;
        min-height: 130px;
        box-shadow: 0 4px 14px rgba(41, 50, 65, 0.04);
    }}

    .praca-name {{
        color: {TEXT};
        font-size: 24px;
        font-weight: 750;
        margin-bottom: 12px;
    }}

    .praca-info {{
        color: {SECONDARY};
        font-size: 13px;
    }}

    .info-card {{
        background: {CARD};
        border: 1px solid {BORDER};
        border-radius: 18px;
        padding: 22px;
        margin-top: 12px;
        box-shadow: 0 4px 14px rgba(41, 50, 65, 0.04);
    }}

    .info-label {{
        color: {SECONDARY};
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 5px;
    }}

    .info-value {{
        color: {TEXT};
        font-size: 16px;
        font-weight: 650;
        margin-bottom: 14px;
    }}

    .score-card {{
        background: {CARD};
        border: 1px solid {BORDER};
        border-radius: 18px;
        padding: 28px;
        min-height: 250px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 0 4px 14px rgba(41, 50, 65, 0.04);
    }}

    .score-label {{
        color: {SECONDARY};
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 12px;
    }}

    .score-value {{
        color: {TEXT};
        font-size: 46px;
        font-weight: 800;
        line-height: 1;
    }}

    .score-description {{
        color: {SECONDARY};
        font-size: 13px;
        margin-top: 12px;
    }}

    .list-card {{
        background: {CARD};
        border: 1px solid {BORDER};
        border-radius: 18px;
        padding: 20px;
        min-height: 180px;
        box-shadow: 0 4px 14px rgba(41, 50, 65, 0.04);
    }}

    .list-title {{
        color: {TEXT};
        font-size: 17px;
        font-weight: 750;
        margin-bottom: 14px;
    }}

    .list-item {{
        border-bottom: 1px solid {BORDER};
        padding: 11px 0;
    }}

    .list-item:last-child {{
        border-bottom: none;
    }}

    .list-name {{
        color: {TEXT};
        font-size: 14px;
        font-weight: 650;
    }}

    .list-function {{
        color: {SECONDARY};
        font-size: 12px;
        margin-top: 3px;
    }}

    .list-score {{
        color: {BLUE};
        font-size: 12px;
        font-weight: 700;
        margin-top: 3px;
    }}

    .empty-message {{
        color: {SECONDARY};
        font-size: 13px;
        padding: 12px 0;
    }}

    .team-card {{
        background: {CARD};
        border: 1px solid {BORDER};
        border-radius: 18px;
        padding: 20px;
        min-height: 150px;
        box-shadow: 0 4px 14px rgba(41, 50, 65, 0.04);
    }}

    .team-name {{
        color: {TEXT};
        font-size: 16px;
        font-weight: 750;
        margin-bottom: 16px;
    }}

    .team-number {{
        color: {TEXT};
        font-size: 28px;
        font-weight: 800;
    }}

    .team-label {{
        color: {SECONDARY};
        font-size: 12px;
    }}

    .status-realizada {{
        color: {GREEN};
        font-size: 13px;
        font-weight: 650;
        margin-top: 14px;
    }}

    .status-pendente {{
        color: {ORANGE};
        font-size: 13px;
        font-weight: 650;
        margin-top: 4px;
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
# BOTÃO ATUALIZAR
# =========================================================

col_atualizacao, col_botao = st.columns([5, 1])

with col_botao:

    if st.button("↻ Atualizar"):

        st.cache_data.clear()
        st.rerun()


# =========================================================
# CARREGAMENTO
# =========================================================

dados_aplicacao = carregar_dados()

data_consulta = datetime.now().strftime(
    "%d/%m/%Y às %H:%M"
)


with col_atualizacao:

    st.caption(
        f"Última atualização dos dados: "
        f"{data_consulta}"
    )


# =========================================================
# VALIDAÇÃO DA ESTRUTURA
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


if len(dados_aplicacao) <= 3:

    st.error(
        "A aba 'Aplicação' não possui dados suficientes "
        "para carregar o dashboard."
    )

    st.stop()


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
# LIMPEZA DOS DADOS
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
    .replace("Júlio", "Julio")
)


# =========================================================
# DATAS
# =========================================================

monitorias_google["Data Monitoria"] = pd.to_datetime(
    monitorias_google["Data Monitoria"],
    dayfirst=True,
    errors="coerce"
)


monitorias_google["Data Lado a Lado"] = pd.to_datetime(
    monitorias_google["Data Lado a Lado"],
    dayfirst=True,
    errors="coerce"
)


monitorias_google["Data Monitoria Offline"] = pd.to_datetime(
    monitorias_google["Data Monitoria Offline"],
    dayfirst=True,
    errors="coerce"
)


# =========================================================
# DUPLICIDADES
# =========================================================

duplicados = (
    monitorias_google[
        monitorias_google["Colaborador"].notna()
    ]
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

            nome_seguro = html.escape(
                str(nome)
            )

            st.write(
                f"- {nome_seguro}: "
                f"{quantidade} registros"
            )


# =========================================================
# FUNÇÕES
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
# AVISO DE FUNÇÕES NÃO IDENTIFICADAS
# =========================================================

nomes_sem_funcao = sorted(
    monitorias_google.loc[
        monitorias_google["Função"] == "Não identificado",
        "Colaborador"
    ]
    .dropna()
    .unique()
    .tolist()
)


if nomes_sem_funcao:

    with st.expander(
        f"⚠️ {len(nomes_sem_funcao)} colaborador(es) "
        "sem função identificada"
    ):

        for nome in nomes_sem_funcao:
            st.write(f"- {nome}")


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
# STATUS DA MONITORIA
# =========================================================

# REGRA OFICIAL:
# Data Monitoria preenchida = monitoria realizada

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


def html_praca(nome, quantidade):

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

        <div class="status-realizada">
            {realizadas} realizadas
        </div>

        <div class="status-pendente">
            {pendentes} pendentes
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

st.caption("NUBE • TREINAMENTO COMERCIAL")

st.title("Dashboard de Monitorias")

st.write(
    "Acompanhamento das aplicações de monitoria"
)


# =========================================================
# FILTROS
# =========================================================

st.subheader("Filtros")

col_filtro_supervisao, col_filtro_status = st.columns(2)


supervisoes = sorted(
    monitorias_google["Supervisão"]
    .dropna()
    .unique()
    .tolist()
)


opcoes_supervisao = [
    "Todas"
] + supervisoes


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
# FILTRO DOS DADOS
# =========================================================

df_filtrado = monitorias_google.copy()


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
# DESEMPENHO GERAL
# =========================================================

st.subheader("Desempenho geral")

st.caption(
    "Média das notas das monitorias"
)


col_grafico, col_score = st.columns(
    [1, 1]
)


notas_validas = df_filtrado[
    df_filtrado["Média"].notna()
]["Média"]


if len(notas_validas) > 0:

    media_geral = notas_validas.mean()

else:

    media_geral = None


if media_geral is not None:

    texto_media = f"{media_geral:.1f}%"

else:

    texto_media = "—"


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
                hole=0.72,
                marker=dict(
                    colors=[
                        BLUE,
                        "#EEF0F7"
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
                    text=f"<b>{texto_media}</b>",
                    x=0.5,
                    y=0.5,
                    font=dict(
                        size=28,
                        color=TEXT
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

    quantidade_com_nota = df_filtrado[
        df_filtrado["Média"].notna()
    ].shape[0]

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

        st.html(
            html_praca(
                nome_praca,
                len(
                    dados_praca[
                        "supervisores"
                    ]
                )
            )
        )


# =========================================================
# CONSULTAR PRAÇA
# =========================================================

st.subheader("Consultar praça")


praca_selecionada = st.selectbox(
    "Selecione uma praça",
    ["Selecione"] + list(pracas.keys())
)


if praca_selecionada != "Selecione":

    dados_praca = pracas[
        praca_selecionada
    ]

    supervisores_texto = "<br>".join(
        html.escape(str(nome))
        for nome in dados_praca["supervisores"]
    )

    responsavel = html.escape(
        str(
            dados_praca["responsavel"]
        )
    )

    st.html(
        f"""
        <div class="info-card">

            <div class="info-label">
                RESPONSÁVEL
            </div>

            <div class="info-value">
                {responsavel}
            </div>

            <div class="info-label">
                SUPERVISORES
            </div>

            <div class="info-value">
                {supervisores_texto}
            </div>

        </div>
        """
    )


# =========================================================
# ACOMPANHAMENTO POR EQUIPE
# =========================================================

st.subheader(
    "Acompanhamento por equipe"
)


if supervisao_selecionada == "Todas":

    nomes_supervisoes = sorted(
        monitorias_google["Supervisão"]
        .dropna()
        .unique()
        .tolist()
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
                monitorias_google[
                    monitorias_google["Supervisão"]
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
        monitorias_google[
            monitorias_google["Supervisão"]
            == supervisao_selecionada
        ].copy()
    )


    if status_selecionado == "Realizadas":

        realizadas_df = df_supervisao[
            df_supervisao["Realizada"]
        ].copy()

        pendentes_df = pd.DataFrame(
            columns=df_supervisao.columns
        )


    elif status_selecionado == "Pendentes":

        realizadas_df = pd.DataFrame(
            columns=df_supervisao.columns
        )

        pendentes_df = df_supervisao[
            ~df_supervisao["Realizada"]
        ].copy()


    else:

        realizadas_df = df_supervisao[
            df_supervisao["Realizada"]
        ].copy()

        pendentes_df = df_supervisao[
            ~df_supervisao["Realizada"]
        ].copy()


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
# LISTA GERAL DE PENDÊNCIAS
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

    col_pend_1, col_pend_2 = st.columns(2)

    metade = (len(pendencias) + 1) // 2

    pendencias_1 = pendencias.iloc[:metade]
    pendencias_2 = pendencias.iloc[metade:]

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
            " <div style='height: 1px;'></div> "
            + html_lista(
                "",
                pendencias_2,
                mostrar_nota=False
            )
        )


# =========================================================
# EVOLUÇÃO DAS MONITORIAS
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
        periodo
        .start_time
    )

    fim_mes = (
        periodo
        .end_time
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
        marker_color=BLUE,
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
# =========================================================

st.subheader(
    "Outras etapas"
)


col_lado, col_offline = (
    st.columns(2)
)


total_lado_a_lado = int(
    monitorias_google[
        "Data Lado a Lado"
    ].notna().sum()
)


total_offline = int(
    monitorias_google[
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
