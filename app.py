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
    monitorias_google["Colaborador"].notna() &
    (monitorias_google["Colaborador"] != "")
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
# CARDS
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
# GRÁFICO MENSAL
# ==========================================

st.markdown(
    f"""
    <div style="
        color:{TEXTO};
        font-size:20px;
        font-weight:600;
        margin-top:25px;
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
    "2026-05",
    "2026-06",
    "2026-07",
    "2026-08",
    "2026-09"
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
