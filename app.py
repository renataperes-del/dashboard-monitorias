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
    page_icon="N",
    layout="wide"
)


# ============================================================
# CORES
# ============================================================

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


# ============================================================
# ESTILO
# ============================================================

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
        background: transparent;
    }}

    [data-testid="stToolbar"] {{
        right: 1rem;
    }}

    h1, h2, h3, h4 {{
        color: {TEXT};
    }}

    .stCaption {{
        color: {SECONDARY};
    }}

    div[data-testid="stMetric"] {{
        background: {CARD};
        border: 1px solid {BORDER};
        border-radius: 16px;
        padding: 18px;
        box-shadow: 0 4px 14px rgba(41, 50, 65, 0.04);
    }}

    div[data-testid="stMetricLabel"] {{
        color: {SECONDARY};
    }}

    div[data-testid="stMetricValue"] {{
        color: {TEXT};
    }}

    div[data-testid="stMetricDelta"] {{
        color: {SECONDARY};
    }}

    .section-space {{
        margin-top: 20px;
    }}

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# CONEXÃO COM GOOGLE SHEETS
# ============================================================

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


# ============================================================
# TRATAMENTO DA PLANILHA
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
# NOTAS DAS MONITORIAS
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
# FUNÇÃO DOS COLABORADORES
# ============================================================

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
)


# ============================================================
# PRAÇAS
# ============================================================

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


# ============================================================
# STATUS
# ============================================================

monitorias_google["Status Monitoria"] = (
    monitorias_google["Data Monitoria"]
    .notna()
    .map({
        True: "Realizada",
        False: "Pendente"
    })
)


# ============================================================
# CABEÇALHO
# ============================================================

st.caption("NUBE • TREINAMENTO COMERCIAL")

st.title("Dashboard de Monitorias")

st.write("Acompanhamento das aplicações de monitoria")


# ============================================================
# FILTRO
# ============================================================

supervisoes = sorted(
    monitorias_google["Supervisão"]
    .dropna()
    .unique()
    .tolist()
)

supervisao_selecionada = st.selectbox(
    "Supervisão",
    ["Todas"] + supervisoes
)

if supervisao_selecionada == "Todas":
    dados = monitorias_google.copy()
else:
    dados = monitorias_google[
        monitorias_google["Supervisão"] == supervisao_selecionada
    ].copy()


# ============================================================
# MÉTRICAS
# ============================================================

total_colaboradores = len(dados)

realizadas = dados["Data Monitoria"].notna().sum()

pendentes = total_colaboradores - realizadas

percentual_concluido = (
    realizadas / total_colaboradores * 100
    if total_colaboradores > 0
    else 0
)

notas_validas = pd.to_numeric(
    dados["Nota Média"],
    errors="coerce"
).dropna()

media_geral = (
    notas_validas.mean()
    if len(notas_validas) > 0
    else 0
)


# ============================================================
# DESEMPENHO GERAL
# ============================================================

st.subheader("Desempenho geral")

st.caption("Média das notas das monitorias")

col_score, col_info = st.columns([1, 2])

with col_score:

    fig_score = go.Figure(
        go.Pie(
            values=[
                media_geral,
                max(100 - media_geral, 0)
            ],
            hole=0.78,
            textinfo="none",
            marker=dict(
                colors=[
                    BLUE,
                    "#EEF0F7"
                ]
            )
        )
    )

    fig_score.update_layout(
        showlegend=False,
        margin=dict(l=10, r=10, t=10, b=10),
        height=220,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        annotations=[
            dict(
                text=f"<b>{media_geral:.1f}%</b>",
                x=0.5,
                y=0.5,
                font=dict(
                    size=30,
                    color=TEXT
                ),
                showarrow=False
            )
        ]
    )

    st.plotly_chart(
        fig_score,
        use_container_width=True,
        config={"displayModeBar": False}
    )

with col_info:

    st.metric(
        "Colaboradores com nota registrada",
        len(notas_validas)
    )


# ============================================================
# CARDS PRINCIPAIS
# ============================================================

st.subheader("Resumo")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "COLABORADORES",
        total_colaboradores
    )

with c2:
    st.metric(
        "REALIZADAS",
        realizadas
    )

with c3:
    st.metric(
        "PENDENTES",
        pendentes
    )

with c4:
    st.metric(
        "% CONCLUÍDO",
        f"{percentual_concluido:.1f}%"
    )


# ============================================================
# PRAÇAS
# ============================================================

st.subheader("Praças e equipes")

st.caption(
    "Selecione uma praça para consultar a distribuição das equipes."
)

cols_pracas = st.columns(4)

for i, (nome_praca, dados_praca) in enumerate(pracas.items()):

    with cols_pracas[i]:

        st.markdown(f"### {nome_praca}")

        st.caption(
            f'{len(dados_praca["supervisores"])} supervisores'
        )


# ============================================================
# SELEÇÃO DE PRAÇA
# ============================================================

praca_selecionada = st.selectbox(
    "Consultar praça",
    ["Todas"] + list(pracas.keys())
)

if praca_selecionada != "Todas":

    dados_praca = pracas[praca_selecionada]

    st.write(
        f"**Responsável:** {dados_praca['responsavel']}"
    )

    st.write(
        "**Supervisores:** "
        + ", ".join(dados_praca["supervisores"])
    )


# ============================================================
# ACOMPANHAMENTO POR EQUIPE
# ============================================================

st.subheader("Acompanhamento por equipe")

st.caption(
    "Consulte quem já realizou e quem ainda está pendente."
)


# ============================================================
# RESUMO POR SUPERVISÃO
# ============================================================

resumo_supervisao = (
    dados.groupby(
        "Supervisão",
        dropna=False
    )
    .agg(
        Colaboradores=("Colaborador", "count"),
        Realizadas=(
            "Data Monitoria",
            lambda x: x.notna().sum()
        )
    )
    .reset_index()
)

resumo_supervisao["Pendentes"] = (
    resumo_supervisao["Colaboradores"]
    - resumo_supervisao["Realizadas"]
)


if supervisao_selecionada == "Todas":

    for inicio in range(0, len(resumo_supervisao), 4):

        grupo = resumo_supervisao.iloc[
            inicio:inicio + 4
        ]

        cols = st.columns(4)

        for i, (_, row) in enumerate(grupo.iterrows()):

            nome = row["Supervisão"]

            if pd.isna(nome):
                nome = "Sem supervisão"

            with cols[i]:

                st.markdown(f"### {nome}")

                st.write(
                    f"Colaboradores: **{int(row['Colaboradores'])}**"
                )

                st.success(
                    f"✓ Realizadas: {int(row['Realizadas'])}"
                )

                st.warning(
                    f"Pendentes: {int(row['Pendentes'])}"
                )

else:

    realizados_nomes = dados[
        dados["Data Monitoria"].notna()
    ]["Colaborador"].tolist()

    pendentes_nomes = dados[
        dados["Data Monitoria"].isna()
    ]["Colaborador"].tolist()

    col_realizadas, col_pendentes = st.columns(2)

    with col_realizadas:

        st.markdown(
            f"### ✓ Realizadas ({len(realizados_nomes)})"
        )

        if realizados_nomes:

            for nome in realizados_nomes:
                st.write(f"• {nome}")

        else:
            st.info(
                "Nenhuma monitoria realizada."
            )

    with col_pendentes:

        st.markdown(
            f"### Pendentes ({len(pendentes_nomes)})"
        )

        if pendentes_nomes:

            for nome in pendentes_nomes:
                st.write(f"• {nome}")

        else:
            st.success(
                "Nenhuma monitoria pendente."
            )


# ============================================================
# EVOLUÇÃO MENSAL
# ============================================================

st.subheader("Evolução das Monitorias")

st.caption(
    "Monitorias realizadas por mês"
)


dados_mensais = dados[
    dados["Data Monitoria"].notna()
].copy()


meses_base = pd.DataFrame({
    "Mês": [
        "2026-05",
        "2026-06",
        "2026-07",
        "2026-08",
        "2026-09"
    ]
})

nomes_meses = {
    "2026-05": "Mai",
    "2026-06": "Jun",
    "2026-07": "Jul",
    "2026-08": "Ago",
    "2026-09": "Set"
}


if not dados_mensais.empty:

    dados_mensais["Mês"] = (
        dados_mensais["Data Monitoria"]
        .dt.to_period("M")
        .astype(str)
    )

    contagem_mensal = (
        dados_mensais
        .groupby("Mês")
        .size()
        .reset_index(name="Monitorias")
    )

else:

    contagem_mensal = pd.DataFrame(
        columns=["Mês", "Monitorias"]
    )


contagem_mensal = meses_base.merge(
    contagem_mensal,
    on="Mês",
    how="left"
)

contagem_mensal["Monitorias"] = (
    contagem_mensal["Monitorias"]
    .fillna(0)
    .astype(int)
)

contagem_mensal["Mês Exibição"] = (
    contagem_mensal["Mês"]
    .map(nomes_meses)
)


fig = go.Figure()

fig.add_trace(
    go.Bar(
        x=contagem_mensal["Mês Exibição"],
        y=contagem_mensal["Monitorias"],
        marker_color=BLUE,
        text=contagem_mensal["Monitorias"],
        textposition="outside",
        hovertemplate=(
            "<b>%{x}</b>"
            "<br>Monitorias: %{y}"
            "<extra></extra>"
        )
    )
)

fig.update_layout(
    height=360,
    margin=dict(
        l=20,
        r=20,
        t=25,
        b=20
    ),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    showlegend=False,
    xaxis=dict(
        title=None,
        showgrid=False,
        tickfont=dict(
            color=SECONDARY
        )
    ),
    yaxis=dict(
        title=None,
        showgrid=True,
        gridcolor=BORDER,
        tickfont=dict(
            color=SECONDARY
        ),
        rangemode="tozero"
    )
)

st.plotly_chart(
    fig,
    use_container_width=True,
    config={"displayModeBar": False}
)


# ============================================================
# OUTRAS ETAPAS
# ============================================================

st.subheader("Outras etapas")

st.caption(
    "Acompanhamento das próximas etapas do processo."
)


lado_a_lado_realizadas = dados[
    dados["Data Lado a Lado"].notna()
].shape[0]

offline_realizadas = dados[
    dados["Data Monitoria Offline"].notna()
].shape[0]


c5, c6 = st.columns(2)

with c5:

    st.metric(
        "LADO A LADO",
        lado_a_lado_realizadas
    )

    if lado_a_lado_realizadas == 0:
        st.caption("Ainda não iniciado")

with c6:

    st.metric(
        "MONITORIA OFFLINE",
        offline_realizadas
    )

    if offline_realizadas == 0:
        st.caption("Ainda não iniciado")
