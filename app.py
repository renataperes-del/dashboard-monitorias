import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import gspread
from google.oauth2.service_account import Credentials

# ==========================================
# CONFIGURAÇÃO
# ==========================================

st.set_page_config(
    page_title="Dashboard de Monitorias",
    page_icon="📊",
    layout="wide"
)

# ==========================================
# CORES
# ==========================================

FUNDO = "#0B0F14"
CARD = "#141A22"
BORDA = "#232B36"
TEXTO = "#F5F7FA"
TEXTO_SECUNDARIO = "#8B96A5"
AZUL = "#4DA3FF"
VERDE = "#35D07F"
LARANJA = "#FFB454"

# ==========================================
# ESTILO
# ==========================================

st.markdown(
    f"""
    <style>

    .stApp {{
        background-color: {FUNDO};
        color: {TEXTO};
    }}

    .card {{
        background-color: {CARD};
        border: 1px solid {BORDA};
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin-bottom: 20px;
    }}

    .card-title {{
        color: {TEXTO_SECUNDARIO};
        font-size: 13px;
        font-weight: 600;
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
        border-radius: 14px;
        padding: 24px;
        min-height: 145px;
        margin-bottom: 15px;
    }}

    .praca-icone {{
        font-size: 30px;
        margin-bottom: 8px;
    }}

    .praca-nome {{
        color: {TEXTO};
        font-size: 19px;
        font-weight: 700;
    }}

    .praca-info {{
        color: {TEXTO_SECUNDARIO};
        font-size: 13px;
        margin-top: 7px;
    }}

    .nome-realizado {{
        background-color: {CARD};
        border: 1px solid {BORDA};
        border-left: 4px solid {VERDE};
        border-radius: 8px;
        padding: 9px 14px;
        margin-bottom: 6px;
        color: {TEXTO};
        font-size: 14px;
    }}

    .nome-pendente {{
        background-color: {CARD};
        border: 1px solid {BORDA};
        border-left: 4px solid {LARANJA};
        border-radius: 8px;
        padding: 9px 14px;
        margin-bottom: 6px;
        color: {TEXTO};
        font-size: 14px;
    }}

    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# CONEXÃO COM GOOGLE SHEETS
# ==========================================

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

# ==========================================
# PREPARAÇÃO DOS DADOS
# ==========================================

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

# ==========================================
# CABEÇALHO
# ==========================================

st.markdown(
    f"""
    <div style="
        color:{AZUL};
        font-size:13px;
        font-weight:600;
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

# ==========================================
# FILTRO
# ==========================================

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

# ==========================================
# FILTRO DOS DADOS
# ==========================================

if supervisao == "Todas":
    dados = monitorias_google.copy()
else:
    dados = monitorias_google[
        monitorias_google["Supervisão"] == supervisao
    ].copy()

# ==========================================
# MÉTRICAS
# ==========================================

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

# ==========================================
# CARDS PRINCIPAIS
# ==========================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">COLABORADORES</div>
            <div class="card-value">{total}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div class="card">
            <div class="card-title" style="color:{VERDE};">
                REALIZADAS
            </div>
            <div class="card-value">{realizadas}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <div class="card">
            <div class="card-title" style="color:{LARANJA};">
                PENDENTES
            </div>
            <div class="card-value">{pendentes}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        f"""
        <div class="card">
            <div class="card-title" style="color:{AZUL};">
                CONCLUÍDO
            </div>
            <div class="card-value">{percentual:.1f}%</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ==========================================
# PRAÇAS E EQUIPES
# ==========================================

st.markdown(
    f"""
    <div style="
        color:{TEXTO};
        font-size:20px;
        font-weight:600;
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

# ==========================================
# DADOS DAS PRAÇAS
# ==========================================

pracas = {
    "São Paulo": {
        "icone": "📍",
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
        "icone": "🌐",
        "responsavel": "Caio Marques",
        "supervisores": [
            "Camila Dias Silva",
            "Laila Cerqueira Rodrigues",
            "Alexssander Affonso da Silva"
        ]
    },

    "Conne-Sul": {
        "icone": "🧭",
        "responsavel": "Evelyn Viegas",
        "supervisores": [
            "Angelica Yumi Gaspar de Oliveira",
            "Karine Conceição Rodrigues"
        ]
    },

    "Sudeste": {
        "icone": "📊",
        "responsavel": "Darlene Carvalho",
        "supervisores": [
            "Maiara Bravo",
            "Letícia da Silva Santos"
        ]
    }
}

# ==========================================
# SELEÇÃO DA PRAÇA
# ==========================================

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

        html_praca = f"""
        <div class="praca-card">

            <div class="praca-icone">
                {dados_praca["icone"]}
            </div>

            <div class="praca-nome">
                {nome_praca}
            </div>

            <div class="praca-info">
                {len(dados_praca["supervisores"])} supervisores
            </div>

        </div>
        """

        st.html(html_praca)

        if st.button(
            f"Consultar {nome_praca}",
            key=f"btn_{nome_praca}",
            use_container_width=True
        ):
            st.session_state.praca_selecionada = nome_praca

# ==========================================
# DETALHAMENTO DA PRAÇA
# ==========================================

if st.session_state.praca_selecionada:

    nome_praca = st.session_state.praca_selecionada
    dados_praca = pracas[nome_praca]

    st.markdown("---")

    st.markdown(
        f"""
        <div style="
            color:{AZUL};
            font-size:22px;
            font-weight:700;
            margin-top:10px;
            margin-bottom:5px;
        ">
            {dados_praca["icone"]} {nome_praca}
        </div>

        <div style="
            color:{TEXTO_SECUNDARIO};
            font-size:14px;
            margin-bottom:20px;
        ">
            Responsável pela praça: <strong>{dados_praca["responsavel"]}</strong>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div style="
            color:{TEXTO};
            font-size:18px;
            font-weight:600;
            margin-bottom:15px;
        ">
            Supervisores da praça
        </div>
        """,
        unsafe_allow_html=True
    )

    col_sup1, col_sup2 = st.columns(2)

    for i, nome in enumerate(dados_praca["supervisores"]):

        with [col_sup1, col_sup2][i % 2]:

            st.markdown(
                f"""
                <div style="
                    background-color:{CARD};
                    border:1px solid {BORDA};
                    border-left:4px solid {AZUL};
                    border-radius:10px;
                    padding:14px 16px;
                    margin-bottom:8px;
                    color:{TEXTO};
                    font-size:14px;
                ">
                    👤 {nome}
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

# ==========================================
# ACOMPANHAMENTO POR EQUIPE
# ==========================================

st.markdown(
    f"""
    <div style="
        color:{TEXTO};
        font-size:20px;
        font-weight:600;
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

# ==========================================
# VISÃO GERAL DE TODAS AS EQUIPES
# ==========================================

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
            border-radius:12px;
            padding:20px;
            margin-bottom:20px;
        ">

            <div style="
                color:{AZUL};
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
            ">
                ✓ Realizadas: {linha["Realizadas"]}
            </div>

            <div style="
                color:{LARANJA};
                font-size:13px;
                margin-top:4px;
            ">
                ⏳ Pendentes: {linha["Pendentes"]}
            </div>

        </div>
        """

        with colunas_resumo[i % 3]:
            st.html(html_card)

# ==========================================
# LISTAS DA SUPERVISÃO SELECIONADA
# ==========================================

else:

    realizadas_lista = (
        dados[
            dados["Data Monitoria"].notna()
        ]
        .sort_values("Colaborador")["Colaborador"]
        .tolist()
    )

    pendentes_lista = (
        dados[
            dados["Data Monitoria"].isna()
        ]
        .sort_values("Colaborador")["Colaborador"]
        .tolist()
    )

    col_realizadas, col_pendentes = st.columns(2)

    # ======================================
    # REALIZADAS
    # ======================================

    with col_realizadas:

        html_realizadas = f"""
        <div style="
            background-color:{CARD};
            border:1px solid {BORDA};
            border-radius:12px;
            padding:20px;
            text-align:center;
            margin-bottom:20px;
        ">

            <div style="
                color:{VERDE};
                font-size:13px;
                font-weight:600;
            ">
                ✓ MONITORIAS REALIZADAS
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

        st.html(html_realizadas)

        if realizadas_lista:

            for nome in realizadas_lista:

                html_nome = f"""
                <div style="
                    background-color:{CARD};
                    border:1px solid {BORDA};
                    border-left:4px solid {VERDE};
                    border-radius:8px;
                    padding:9px 14px;
                    margin-bottom:6px;
                    color:{TEXTO};
                    font-size:14px;
                ">
                    ✓ {nome}
                </div>
                """

                st.html(html_nome)

        else:

            st.info(
                "Nenhuma monitoria realizada."
            )

    # ======================================
    # PENDENTES
    # ======================================

    with col_pendentes:

        html_pendentes = f"""
        <div style="
            background-color:{CARD};
            border:1px solid {BORDA};
            border-radius:12px;
            padding:20px;
            text-align:center;
            margin-bottom:20px;
        ">

            <div style="
                color:{LARANJA};
                font-size:13px;
                font-weight:600;
            ">
                ⏳ MONITORIAS PENDENTES
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

        st.html(html_pendentes)

        if pendentes_lista:

            for nome in pendentes_lista:

                html_nome = f"""
                <div style="
                    background-color:{CARD};
                    border:1px solid {BORDA};
                    border-left:4px solid {LARANJA};
                    border-radius:8px;
                    padding:9px 14px;
                    margin-bottom:6px;
                    color:{TEXTO};
                    font-size:14px;
                ">
                    ⏳ {nome}
                </div>
                """

                st.html(html_nome)

        else:

            st.success(
                "Todas as monitorias foram realizadas."
            )

# ==========================================
# GRÁFICO MENSAL
# ==========================================

st.markdown(
    f"""
    <div style="
        color:{TEXTO};
        font-size:20px;
        font-weight:600;
        margin-top:30px;
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
            "color": TEXTO,
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
    use_container_width=True
)
