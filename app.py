import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import gspread
from google.oauth2.service_account import Credentials


# =========================================================
# CONFIGURAÇÃO
# =========================================================

st.set_page_config(
    page_title="Dashboard de Monitorias",
    page_icon="N",
    layout="wide"
)

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

    /* -------------------------------------------------- */
    /* CARDS                                                */
    /* -------------------------------------------------- */

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

    .custom-card-name {{
        color: {TEXT};
        font-size: 18px;
        font-weight: 700;
        margin-bottom: 8px;
    }}

    .custom-card-subtitle {{
        color: {SECONDARY};
        font-size: 13px;
    }}

    /* -------------------------------------------------- */
    /* PRAÇAS                                               */
    /* -------------------------------------------------- */

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

    /* -------------------------------------------------- */
    /* INFORMAÇÕES                                          */
    /* -------------------------------------------------- */

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

    /* -------------------------------------------------- */
    /* NOTA GERAL                                           */
    /* -------------------------------------------------- */

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

    /* -------------------------------------------------- */
    /* LISTAS                                               */
    /* -------------------------------------------------- */

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

    /* -------------------------------------------------- */
    /* SUPERVISÃO                                           */
    /* -------------------------------------------------- */

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
    }}

    .status-pendente {{
        color: {ORANGE};
        font-size: 13px;
        font-weight: 650;
    }}

    /* -------------------------------------------------- */
    /* SEPARADORES                                          */
    /* -------------------------------------------------- */

    .section-space {{
        height: 12px;
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

credenciais = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
)

gc = gspread.authorize(credenciais)

planilha = gc.open_by_key(SHEET_ID)
aba_aplicacao = planilha.worksheet(ABA)

dados_aplicacao = aba_aplicacao.get_all_values()


# =========================================================
# DATAFRAME
# =========================================================

monitorias_google = pd.DataFrame(dados_aplicacao)

monitorias_google = monitorias_google.iloc[3:].copy()

monitorias_google.columns = [
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

monitorias_google = monitorias_google[
    monitorias_google["Colaborador"].notna()
    & (monitorias_google["Colaborador"] != "")
].copy()

monitorias_google = monitorias_google.replace("", pd.NA)

monitorias_google["Supervisão"] = (
    monitorias_google["Supervisão"]
    .replace("Júlio", "Julio")
)

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
# Monitoria realizada = Data Monitoria preenchida

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
# FUNÇÕES AUXILIARES
# =========================================================

def html_card(titulo, valor, subtitulo=""):
    return f"""
    <div class="custom-card">
        <div class="custom-card-title">{titulo}</div>
        <div class="custom-card-value">{valor}</div>
        <div class="custom-card-subtitle">{subtitulo}</div>
    </div>
    """


def html_praca(nome, quantidade):
    return f"""
    <div class="praca-card">
        <div class="praca-name">{nome}</div>
        <div class="praca-info">
            {quantidade} supervisões
        </div>
    </div>
    """


def html_team(nome, total, realizadas, pendentes):
    return f"""
    <div class="team-card">
        <div class="team-name">{nome}</div>

        <div class="team-number">{total}</div>
        <div class="team-label">colaboradores</div>

        <div style="margin-top:14px;">
            <div class="status-realizada">
                {realizadas} realizadas
            </div>

            <div class="status-pendente">
                {pendentes} pendentes
            </div>
        </div>
    </div>
    """


def html_lista(titulo, dataframe, mostrar_nota=True):

    if dataframe.empty:
        return f"""
        <div class="list-card">
            <div class="list-title">{titulo}</div>
            <div class="empty-message">
                Nenhum colaborador nesta categoria.
            </div>
        </div>
        """

    itens = ""

    for _, row in dataframe.iterrows():

        nome = row["Colaborador"]
        funcao = row["Função"]

        media = row["Média"]

        nota_html = ""

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

st.caption("NUBE • TREINAMENTO COMERCIAL")

st.title("Dashboard de Monitorias")

st.write(
    "Acompanhamento das aplicações de monitoria"
)


# =========================================================
# FILTRO
# =========================================================

supervisoes = sorted(
    monitorias_google["Supervisão"]
    .dropna()
    .unique()
    .tolist()
)

opcoes_supervisao = ["Todas"] + supervisoes

supervisao_selecionada = st.selectbox(
    "Supervisão",
    opcoes_supervisao
)


# =========================================================
# DATAFRAME FILTRADO
# =========================================================

if supervisao_selecionada == "Todas":

    df_filtrado = monitorias_google.copy()

else:

    df_filtrado = monitorias_google[
        monitorias_google["Supervisão"]
        == supervisao_selecionada
    ].copy()


# =========================================================
# DESEMPENHO GERAL
# =========================================================

st.subheader("Desempenho geral")

st.caption("Média das notas das monitorias")

col_grafico, col_score = st.columns([1, 1])


notas_validas = df_filtrado[
    df_filtrado["Média"].notna()
]["Média"]

if len(notas_validas) > 0:

    media_geral = notas_validas.mean()

else:

    media_geral = 0


with col_grafico:

    fig = go.Figure(
        go.Pie(
            values=[
                media_geral,
                max(0, 100 - media_geral)
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
                text=f"<b>{media_geral:.1f}%</b>",
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

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False}
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

total_colaboradores = len(df_filtrado)

total_realizadas = int(
    df_filtrado["Realizada"].sum()
)

total_pendentes = (
    total_colaboradores
    - total_realizadas
)

percentual_concluido = (
    total_realizadas / total_colaboradores * 100
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

for coluna, (nome_praca, dados_praca) in zip(
    colunas_pracas,
    pracas.items()
):

    with coluna:

        st.html(
            html_praca(
                nome_praca,
                len(dados_praca["supervisores"])
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

    dados_praca = pracas[praca_selecionada]

    supervisores_texto = "<br>".join(
        dados_praca["supervisores"]
    )

    st.html(
        f"""
        <div class="info-card">

            <div class="info-label">
                RESPONSÁVEL
            </div>

            <div class="info-value">
                {dados_praca["responsavel"]}
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

st.subheader("Acompanhamento por equipe")


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

            df_supervisao = monitorias_google[
                monitorias_google["Supervisão"]
                == supervisao
            ]

            total = len(df_supervisao)

            realizadas = int(
                df_supervisao["Realizada"].sum()
            )

            pendentes = (
                total - realizadas
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

    df_supervisao = monitorias_google[
        monitorias_google["Supervisão"]
        == supervisao_selecionada
    ].copy()

    realizadas_df = df_supervisao[
        df_supervisao["Realizada"]
    ].copy()

    pendentes_df = df_supervisao[
        ~df_supervisao["Realizada"]
    ].copy()

    col_realizadas, col_pendentes = st.columns(2)

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
# EVOLUÇÃO DAS MONITORIAS
# =========================================================

st.subheader("Evolução das Monitorias")

meses = pd.date_range(
    "2026-05-01",
    "2026-09-01",
    freq="MS"
)

nomes_meses = [
    "Mai",
    "Jun",
    "Jul",
    "Ago",
    "Set"
]

quantidades = []

for mes in meses:

    proximo_mes = mes + pd.offsets.MonthBegin(1)

    quantidade = monitorias_google[
        (
            monitorias_google["Data Monitoria"] >= mes
        )
        &
        (
            monitorias_google["Data Monitoria"] < proximo_mes
        )
    ].shape[0]

    quantidades.append(quantidade)


fig_evolucao = go.Figure()

fig_evolucao.add_trace(
    go.Bar(
        x=nomes_meses,
        y=quantidades,
        marker_color=BLUE,
        text=quantidades,
        textposition="outside",
        hovertemplate="%{x}: %{y} monitorias<extra></extra>"
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
        gridcolor="#E8EAF2",
        zeroline=False
    ),
    showlegend=False
)

st.plotly_chart(
    fig_evolucao,
    use_container_width=True,
    config={"displayModeBar": False}
)


# =========================================================
# OUTRAS ETAPAS
# =========================================================

st.subheader("Outras etapas")

col_lado, col_offline = st.columns(2)


total_lado_a_lado = int(
    monitorias_google["Data Lado a Lado"]
    .notna()
    .sum()
)

total_offline = int(
    monitorias_google["Data Monitoria Offline"]
    .notna()
    .sum()
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
