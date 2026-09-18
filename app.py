import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import gspread
from google.oauth2.service_account import Credentials


# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="Dashboard de Monitorias",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# PALETA
# ============================================================

FUNDO = "#F7F8FC"
CARD = "#FFFFFF"
BORDA = "#E8EAF2"

TEXTO = "#293241"
TEXTO_SECUNDARIO = "#7B8496"

AZUL = "#5B7CFA"
ROXO = "#8B7CF6"
VERDE = "#55B99D"
LARANJA = "#F2A66F"
ROSA = "#E58FA3"


# ============================================================
# CSS
# ============================================================

st.markdown(
    f"""
    <style>

    .stApp {{
        background-color: {FUNDO};
        color: {TEXTO};
    }}

    .main .block-container {{
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }}

    h1, h2, h3 {{
        color: {TEXTO} !important;
    }}

    .stSelectbox label {{
        color: {TEXTO} !important;
        font-weight: 600;
    }}

    .card {{
        background-color: {CARD};
        border: 1px solid {BORDA};
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 16px rgba(41, 50, 65, 0.05);
    }}

    .card-title {{
        color: {TEXTO_SECUNDARIO};
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.5px;
    }}

    .card-value {{
        color: {TEXTO};
        font-size: 32px;
        font-weight: 700;
        margin-top: 5px;
    }}

    .praca-card {{
        background-color: {CARD};
        border: 1px solid {BORDA};
        border-radius: 16px;
        padding: 24px;
        min-height: 125px;
        margin-bottom: 10px;
        box-shadow: 0 4px 16px rgba(41, 50, 65, 0.05);
    }}

    .praca-nome {{
        color: {TEXTO};
        font-size: 23px;
        font-weight: 700;
    }}

    .praca-info {{
        color: {TEXTO_SECUNDARIO};
        font-size: 13px;
        margin-top: 8px;
    }}

    .nome-realizado {{
        background-color: {CARD};
        border: 1px solid {BORDA};
        border-left: 4px solid {VERDE};
        border-radius: 10px;
        padding: 11px 15px;
        margin-bottom: 7px;
        color: {TEXTO};
        font-size: 14px;
        box-shadow: 0 2px 8px rgba(41, 50, 65, 0.03);
    }}

    .nome-pendente {{
        background-color: {CARD};
        border: 1px solid {BORDA};
        border-left: 4px solid {LARANJA};
        border-radius: 10px;
        padding: 11px 15px;
        margin-bottom: 7px;
        color: {TEXTO};
        font-size: 14px;
        box-shadow: 0 2px 8px rgba(41, 50, 65, 0.03);
    }}

    .funcao {{
        color: {TEXTO_SECUNDARIO};
        font-size: 12px;
        margin-top: 4px;
    }}

    .nota {{
        color: {ROXO};
        font-size: 12px;
        font-weight: 700;
        margin-top: 3px;
    }}

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# GOOGLE SHEETS
# ============================================================

credenciais = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
)

gc = gspread.authorize(credenciais)

planilha = gc.open_by_key(
    "1bSYqD9wLkpMxTIGN6kyFh6zuVTixM384oQr8cGskYcM"
)

aba_aplicacao = planilha.worksheet("Aplicação")

dados_aplicacao = aba_aplicacao.get_all_values()


# ============================================================
# PREPARAÇÃO DOS DADOS DA PLANILHA
# ============================================================

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


# ============================================================
# FUNÇÕES DOS COLABORADORES
# ============================================================

execs = {
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
}

apoio_adm = {
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
}


def identificar_funcao(nome):

    if nome in execs:
        return "Exec"

    if nome in apoio_adm:
        return "Apoio ADM"

    return ""


monitorias_google["Função"] = (
    monitorias_google["Colaborador"]
    .apply(identificar_funcao)
)


# ============================================================
# NOTAS DAS MONITORIAS
#
# Fonte: tabela de notas enviada pela Renata.
#
# Cada pessoa possui:
# [nota ligação 1, nota ligação 2]
#
# Se existir somente uma nota, ela será usada.
# ============================================================

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

    notas = notas_monitoria.get(nome)

    if not notas:
        return pd.NA

    notas_validas = []

    for nota in notas:

        if nota is not None:

            try:
                notas_validas.append(float(nota))
            except:
                pass

    if not notas_validas:
        return pd.NA

    return sum(notas_validas) / len(notas_validas)


monitorias_google["Nota Média"] = (
    monitorias_google["Colaborador"]
    .apply(calcular_media_notas)
)


# ============================================================
# CABEÇALHO
# ============================================================

st.markdown(
    f"""
    <div style="
        color:{AZUL};
        font-size:13px;
        font-weight:700;
        letter-spacing:1px;
        margin-bottom:4px;
    ">
        NUBE • TREINAMENTO COMERCIAL
    </div>
    """,
    unsafe_allow_html=True
)

st.title("Dashboard de Monitorias")

st.caption(
    "Acompanhamento das aplicações de monitoria"
)


# ============================================================
# FILTRO DE SUPERVISÃO
# ============================================================

supervisoes = ["Todas"] + sorted(
    monitorias_google["Supervisão"]
    .dropna()
    .unique()
    .tolist()
)

supervisao = st.selectbox(
    "Supervisão",
    supervisoes
)


# ============================================================
# DADOS FILTRADOS
# ============================================================

if supervisao == "Todas":

    dados = monitorias_google.copy()

else:

    dados = monitorias_google[
        monitorias_google["Supervisão"] == supervisao
    ].copy()


# ============================================================
# MÉTRICAS
# ============================================================

total = len(dados)

realizadas = dados[
    dados["Data Monitoria"].notna()
].shape[0]

pendentes = total - realizadas

percentual = (
    realizadas / total * 100
    if total > 0
    else 0
)


# ============================================================
# MÉDIA DAS NOTAS
# ============================================================

notas_validas = pd.to_numeric(
    dados["Nota Média"],
    errors="coerce"
).dropna()

media_notas = (
    notas_validas.mean()
    if len(notas_validas) > 0
    else 0
)


# ============================================================
# DESEMPENHO GERAL
# ============================================================

st.markdown(
    f"""
    <div style="
        text-align:center;
        margin-top:15px;
        margin-bottom:-10px;
    ">

        <div style="
            color:{TEXTO};
            font-size:22px;
            font-weight:700;
        ">
            Desempenho geral
        </div>

        <div style="
            color:{TEXTO_SECUNDARIO};
            font-size:13px;
            margin-top:4px;
        ">
            Média das notas das monitorias
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


fig_circulo = go.Figure(
    go.Pie(
        values=[
            media_notas,
            max(100 - media_notas, 0)
        ],
        hole=0.78,
        marker=dict(
            colors=[
                AZUL,
                "#E9EBF5"
            ],
            line=dict(
                color=FUNDO,
                width=2
            )
        ),
        textinfo="none",
        hoverinfo="skip",
        sort=False
    )
)

fig_circulo.add_annotation(
    text=f"<b>{media_notas:.1f}%</b>",
    x=0.5,
    y=0.5,
    showarrow=False,
    font=dict(
        color=TEXTO,
        size=30
    )
)

fig_circulo.update_layout(
    paper_bgcolor=FUNDO,
    plot_bgcolor=FUNDO,
    height=270,
    margin=dict(
        l=0,
        r=0,
        t=5,
        b=5
    ),
    showlegend=False
)


col_circulo1, col_circulo2, col_circulo3 = st.columns(
    [1, 1.2, 1]
)

with col_circulo2:

    st.plotly_chart(
        fig_circulo,
        use_container_width=True,
        config={
            "displayModeBar": False
        }
    )


st.markdown(
    f"""
    <div style="
        text-align:center;
        color:{TEXTO_SECUNDARIO};
        font-size:12px;
        margin-top:-25px;
        margin-bottom:25px;
    ">
        {len(notas_validas)} colaborador(es) com nota registrada
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# CARDS PRINCIPAIS
# ============================================================

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.markdown(
        f"""
        <div class="card">

            <div class="card-title">
                COLABORADORES
            </div>

            <div class="card-value">
                {total}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


with col2:

    st.markdown(
        f"""
        <div class="card">

            <div class="card-title"
                 style="color:{VERDE};">
                REALIZADAS
            </div>

            <div class="card-value">
                {realizadas}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


with col3:

    st.markdown(
        f"""
        <div class="card">

            <div class="card-title"
                 style="color:{LARANJA};">
                PENDENTES
            </div>

            <div class="card-value">
                {pendentes}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


with col4:

    st.markdown(
        f"""
        <div class="card">

            <div class="card-title"
                 style="color:{ROXO};">
                CONCLUÍDO
            </div>

            <div class="card-value">
                {percentual:.1f}%
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# PRAÇAS
# ============================================================

st.markdown(
    f"""
    <div style="
        color:{TEXTO};
        font-size:21px;
        font-weight:700;
        margin-top:30px;
        margin-bottom:5px;
    ">
        Praças e equipes
    </div>

    <div style="
        color:{TEXTO_SECUNDARIO};
        font-size:13px;
        margin-bottom:15px;
    ">
        Selecione uma praça para consultar a distribuição das equipes.
    </div>
    """,
    unsafe_allow_html=True
)


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


if "praca_selecionada" not in st.session_state:

    st.session_state.praca_selecionada = None


col_praca1, col_praca2 = st.columns(2)
col_praca3, col_praca4 = st.columns(2)


botoes_pracas = [
    (col_praca1, "São Paulo"),
    (col_praca2, "GMSP"),
    (col_praca3, "Conne-Sul"),
    (col_praca4, "Sudeste")
]


for coluna, nome_praca in botoes_pracas:

    dados_praca = pracas[nome_praca]

    with coluna:

        st.html(
            f"""
            <div class="praca-card">

                <div class="praca-nome">
                    {nome_praca}
                </div>

                <div class="praca-info">
                    {len(dados_praca["supervisores"])} supervisores
                </div>

            </div>
            """
        )

        if st.button(
            f"Consultar {nome_praca}",
            key=f"btn_{nome_praca}",
            use_container_width=True
        ):

            st.session_state.praca_selecionada = nome_praca


# ============================================================
# DETALHAMENTO DA PRAÇA
# ============================================================

if st.session_state.praca_selecionada:

    nome_praca = st.session_state.praca_selecionada

    dados_praca = pracas[nome_praca]

    st.markdown("---")

    st.markdown(
        f"""
        <div style="
            color:{AZUL};
            font-size:25px;
            font-weight:700;
            margin-top:10px;
            margin-bottom:5px;
        ">
            {nome_praca}
        </div>

        <div style="
            color:{TEXTO_SECUNDARIO};
            font-size:14px;
            margin-bottom:20px;
        ">
            Responsável pela praça:
            <strong>{dados_praca["responsavel"]}</strong>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div style="
            color:{TEXTO};
            font-size:18px;
            font-weight:700;
            margin-bottom:15px;
        ">
            Supervisores da praça
        </div>
        """,
        unsafe_allow_html=True
    )

    col_sup1, col_sup2 = st.columns(2)

    for i, nome in enumerate(
        dados_praca["supervisores"]
    ):

        with [col_sup1, col_sup2][i % 2]:

            st.markdown(
                f"""
                <div style="
                    background-color:{CARD};
                    border:1px solid {BORDA};
                    border-left:4px solid {ROXO};
                    border-radius:10px;
                    padding:14px 16px;
                    margin-bottom:8px;
                    color:{TEXTO};
                    font-size:14px;
                    box-shadow:0 2px 8px rgba(41,50,65,0.03);
                ">
                    {nome}
                </div>
                """,
                unsafe_allow_html=True
            )

    if st.button(
        "← Voltar para praças",
        key="voltar_pracas"
    ):

        st.session_state.praca_selecionada = None

        st.rerun()


# ============================================================
# ACOMPANHAMENTO POR EQUIPE
# ============================================================

st.markdown(
    f"""
    <div style="
        color:{TEXTO};
        font-size:21px;
        font-weight:700;
        margin-top:30px;
        margin-bottom:5px;
    ">
        Acompanhamento por equipe
    </div>

    <div style="
        color:{TEXTO_SECUNDARIO};
        font-size:13px;
        margin-bottom:15px;
    ">
        Consulte quem já realizou e quem ainda está pendente.
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# TODAS AS EQUIPES
# ============================================================

if supervisao == "Todas":

    resumo_equipes = (
        monitorias_google
        .assign(
            Status=monitorias_google["Data Monitoria"].notna()
        )
        .groupby("Supervisão")
        .agg(
            Colaboradores=("Colaborador", "count"),
            Realizadas=("Status", "sum")
        )
        .reset_index()
    )

    resumo_equipes["Pendentes"] = (
        resumo_equipes["Colaboradores"]
        - resumo_equipes["Realizadas"]
    )

    resumo_equipes = resumo_equipes.sort_values(
        "Supervisão"
    )

    colunas_resumo = st.columns(3)

    for i, (_, linha) in enumerate(
        resumo_equipes.iterrows()
    ):

        html_card = f"""
        <div style="
            background-color:{CARD};
            border:1px solid {BORDA};
            border-radius:14px;
            padding:20px;
            margin-bottom:20px;
            box-shadow:0 4px 14px rgba(41,50,65,0.04);
        ">

            <div style="
                color:{ROXO};
                font-size:17px;
                font-weight:700;
                margin-bottom:12px;
            ">
                {linha["Supervisão"]}
            </div>

            <div style="
                color:{TEXTO_SECUNDARIO};
                font-size:13px;
            ">
                Colaboradores
            </div>

            <div style="
                color:{TEXTO};
                font-size:22px;
                font-weight:700;
            ">
                {linha["Colaboradores"]}
            </div>

            <div style="
                color:{VERDE};
                font-size:13px;
                margin-top:8px;
                font-weight:600;
            ">
                ✓ Realizadas: {linha["Realizadas"]}
            </div>

            <div style="
                color:{LARANJA};
                font-size:13px;
                margin-top:4px;
                font-weight:600;
            ">
                Pendentes: {linha["Pendentes"]}
            </div>

        </div>
        """

        with colunas_resumo[i % 3]:

            st.html(html_card)


# ============================================================
# SUPERVISÃO SELECIONADA
# ============================================================

else:

    realizadas_lista = (
        dados[
            dados["Data Monitoria"].notna()
        ]
        .sort_values("Colaborador")
        .to_dict("records")
    )

    pendentes_lista = (
        dados[
            dados["Data Monitoria"].isna()
        ]
        .sort_values("Colaborador")
        .to_dict("records")
    )

    col_realizadas, col_pendentes = st.columns(2)


    # ========================================================
    # REALIZADAS
    # ========================================================

    with col_realizadas:

        st.html(
            f"""
            <div style="
                background-color:{CARD};
                border:1px solid {BORDA};
                border-radius:14px;
                padding:20px;
                text-align:center;
                margin-bottom:20px;
                box-shadow:0 4px 14px rgba(41,50,65,0.04);
            ">

                <div style="
                    color:{VERDE};
                    font-size:13px;
                    font-weight:700;
                ">
                    MONITORIAS REALIZADAS
                </div>

                <div style="
                    color:{TEXTO};
                    font-size:32px;
                    font-weight:700;
                    margin-top:5px;
                ">
                    {len(realizadas_lista)}
                </div>

            </div>
            """
        )

        if realizadas_lista:

            for registro in realizadas_lista:

                nome = registro["Colaborador"]
                funcao = registro["Função"]
                nota = registro["Nota Média"]

                funcao_html = ""

                if funcao:

                    funcao_html = f"""
                    <div class="funcao">
                        {funcao}
                    </div>
                    """

                nota_html = ""

                if pd.notna(nota):

                    nota_html = f"""
                    <div class="nota">
                        Nota: {nota:.1f}%
                    </div>
                    """

                st.html(
                    f"""
                    <div class="nome-realizado">

                        <div>
                            ✓ {nome}
                        </div>

                        {funcao_html}

                        {nota_html}

                    </div>
                    """
                )

        else:

            st.info(
                "Nenhuma monitoria realizada."
            )


    # ========================================================
    # PENDENTES
    # ========================================================

    with col_pendentes:

        st.html(
            f"""
            <div style="
                background-color:{CARD};
                border:1px solid {BORDA};
                border-radius:14px;
                padding:20px;
                text-align:center;
                margin-bottom:20px;
                box-shadow:0 4px 14px rgba(41,50,65,0.04);
            ">

                <div style="
                    color:{LARANJA};
                    font-size:13px;
                    font-weight:700;
                ">
                    MONITORIAS PENDENTES
                </div>

                <div style="
                    color:{TEXTO};
                    font-size:32px;
                    font-weight:700;
                    margin-top:5px;
                ">
                    {len(pendentes_lista)}
                </div>

            </div>
            """
        )

        if pendentes_lista:

            for registro in pendentes_lista:

                nome = registro["Colaborador"]
                funcao = registro["Função"]

                funcao_html = ""

                if funcao:

                    funcao_html = f"""
                    <div class="funcao">
                        {funcao}
                    </div>
                    """

                st.html(
                    f"""
                    <div class="nome-pendente">

                        <div>
                            {nome}
                        </div>

                        {funcao_html}

                    </div>
                    """
                )

        else:

            st.success(
                "Todas as monitorias foram realizadas."
            )


# ============================================================
# EVOLUÇÃO MENSAL
# ============================================================

st.markdown(
    f"""
    <div style="
        color:{TEXTO};
        font-size:21px;
        font-weight:700;
        margin-top:35px;
        margin-bottom:5px;
    ">
        Evolução das Monitorias
    </div>

    <div style="
        color:{TEXTO_SECUNDARIO};
        font-size:13px;
        margin-bottom:10px;
    ">
        Monitorias realizadas por mês
    </div>
    """,
    unsafe_allow_html=True
)


dados_com_data = dados[
    dados["Data Monitoria"].notna()
].copy()


contagem_mensal = (
    dados_com_data
    .groupby(
        dados_com_data["Data Monitoria"].dt.to_period("M")
    )
    .size()
)


periodos = [
    pd.Period("2026-05", freq="M"),
    pd.Period("2026-06", freq="M"),
    pd.Period("2026-07", freq="M"),
    pd.Period("2026-08", freq="M"),
    pd.Period("2026-09", freq="M")
]


meses = [
    "Maio",
    "Junho",
    "Julho",
    "Agosto",
    "Setembro"
]


valores = [
    contagem_mensal.get(periodo, 0)
    for periodo in periodos
]


fig = go.Figure()

fig.add_trace(
    go.Bar(
        x=meses,
        y=valores,
        marker_color=AZUL,
        text=valores,
        textposition="inside",
        textfont={
            "color": "#FFFFFF",
            "size": 13
        },
        hovertemplate=(
            "<b>%{x}</b><br>"
            "%{y} monitorias"
            "<extra></extra>"
        )
    )
)


fig.update_layout(
    paper_bgcolor=FUNDO,
    plot_bgcolor=FUNDO,
    font={
        "family": "Arial",
        "color": TEXTO
    },
    height=400,
    margin=dict(
        l=50,
        r=30,
        t=20,
        b=50
    ),
    showlegend=False
)


fig.update_xaxes(
    showgrid=False,
    color=TEXTO_SECUNDARIO
)


fig.update_yaxes(
    showgrid=True,
    gridcolor=BORDA,
    color=TEXTO_SECUNDARIO,
    zeroline=False,
    range=[0, 32],
    dtick=5
)


st.plotly_chart(
    fig,
    use_container_width=True,
    config={
        "displayModeBar": False
    }
)
