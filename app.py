from datetime import datetime
import html
import unicodedata
from zoneinfo import ZoneInfo

from google.oauth2.service_account import Credentials
import gspread
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# =========================================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================================

st.set_page_config(
    page_title="Dashboard de Monitorias",
    page_icon="📊",
    layout="wide"
)

# =========================================================
# PALETA DE CORES E ESTILOS CSS INSPIRADOS NO DESIGN
# =========================================================

BG_APP = "#E2E7F0"          # Fundo geral cinza/azulado claro
SIDEBAR_BG = "#5A6B8B"      # Sidebar azul-slate
CARD_BG = "#FFFFFF"         # Cards brancos
TEXT_MAIN = "#334155"       # Texto principal
TEXT_MUTED = "#94A3B8"      # Texto secundário/subtítulos

# Cores vibrantes do layout
COLOR_BLUE = "#1E90FF"
COLOR_YELLOW = "#FFB300"
COLOR_GREEN = "#20B2AA"
COLOR_RED = "#FF5252"
COLOR_PURPLE = "#9C27B0"

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* Fundo da aplicação */
    .stApp {{
        background-color: {BG_APP};
        color: {TEXT_MAIN};
        font-family: 'Inter', sans-serif;
    }}

    .block-container {{
        max-width: none;
        padding: 1.5rem 2rem 2rem 2rem;
    }}

    #MainMenu, footer {{ visibility: hidden; }}
    [data-testid="stHeader"] {{ background: transparent !important; }}

    /* Estilização da Sidebar Lateral */
    [data-testid="stSidebar"] {{
        background-color: {SIDEBAR_BG} !important;
    }}
    
    [data-testid="stSidebar"] * {{
        color: #FFFFFF !important;
    }}

    .sidebar-title {{
        font-size: 20px;
        font-weight: 800;
        letter-spacing: 0.05em;
        margin-bottom: 25px;
        padding-left: 5px;
    }}

    .sidebar-section-title {{
        font-size: 11px;
        color: #CBD5E1 !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-top: 25px;
        margin-bottom: 10px;
        padding-left: 5px;
    }}

    /* Barra Superior (Search Header) */
    .search-bar-container {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 12px;
    }}

    .search-input-fake {{
        background: #FFFFFF;
        border-radius: 20px;
        padding: 8px 20px;
        width: 320px;
        font-size: 13px;
        color: #94A3B8;
        box-shadow: 0 2px 5px rgba(0,0,0,0.03);
        display: flex;
        align-items: center;
        gap: 8px;
    }}

    .user-profile-fake {{
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 13px;
        color: #64748B;
        font-weight: 600;
    }}

    .breadcrumb-text {{
        font-size: 12px;
        color: #94A3B8;
        margin-bottom: 15px;
    }}

    /* Estilo Base dos Cards */
    .ui-card {{
        background: {CARD_BG};
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        height: 100%;
        box-sizing: border-box;
    }}

    .ui-card-title {{
        font-size: 12px;
        font-weight: 700;
        color: #94A3B8;
        margin-bottom: 8px;
    }}

    /* Cards de Métricas com Gráfico Embutido */
    .metric-card-custom {{
        background: {CARD_BG};
        border-radius: 12px;
        padding: 16px 18px 0px 18px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        overflow: hidden;
        position: relative;
    }}

    .metric-card-title {{
        font-size: 13px;
        font-weight: 600;
        color: #64748B;
        text-align: center;
    }}

    .metric-card-value {{
        font-size: 24px;
        font-weight: 800;
        text-align: center;
        margin-top: 4px;
        margin-bottom: 2px;
    }}

    .metric-card-sub {{
        font-size: 10px;
        color: #CBD5E1;
        text-align: center;
        margin-bottom: 10px;
    }}

    /* Lista "Recently News" / Atividades */
    .news-item {{
        padding: 8px 0;
        border-bottom: 1px solid #F1F5F9;
    }}
    .news-item:last-child {{
        border-bottom: none;
    }}
    .news-header {{
        display: flex;
        justify-content: space-between;
        font-size: 10px;
        font-weight: 700;
        color: #1E90FF;
    }}
    .news-time {{
        color: #94A3B8;
        font-weight: 500;
    }}
    .news-desc {{
        font-size: 10px;
        color: #64748B;
        margin-top: 3px;
        line-height: 1.3;
    }}

    /* Ajustes Gerais do Streamlit */
    .stButton > button {{
        border-radius: 8px;
        border: none;
        background: #1E90FF;
        color: white;
        font-weight: 600;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# CONEXÃO E CARREGAMENTO DE DADOS
# =========================================================

SHEET_ID = "1bSYqD9wLkpMxTIGN6kyFh6zuVTixM384oQr8cGskYcM"
ABA = "Aplicação"

@st.cache_resource
def get_client():
    credenciais = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
    )
    return gspread.authorize(credenciais)

@st.cache_data(ttl=300)
def carregar_dados():
    try:
        gc = get_client()
        planilha = gc.open_by_key(SHEET_ID)
        aba_aplicacao = planilha.worksheet(ABA)
        valores = aba_aplicacao.get_all_values()
        horario = datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%H:%M")
        return valores, horario
    except Exception as e:
        raise RuntimeError("Erro ao conectar com a planilha.") from e

try:
    dados_aplicacao, data_consulta = carregar_dados()
except RuntimeError as erro:
    st.error(str(erro))
    st.stop()

# =========================================================
# PROCESSAMENTO DE DADOS COM PANDAS
# =========================================================

MAPEAMENTO_COLUNAS = {
    0: "Colaborador",
    1: "Supervisão",
    2: "Data Monitoria",
    3: "Quem Aplicou Monitoria",
    4: "Ligação 1",
    5: "Ligação 2",
    6: "Data Lado a Lado",
    7: "Quem Aplicou Lado a Lado",
    8: "Observação Lado a Lado",
    9: "Data Monitoria Offline",
    10: "Quem Aplicou Offline",
    11: "Percentual Offline",
    12: "Observações Gerais"
}

def normalizar_texto(valor):
    if pd.isna(valor):
        return ""
    texto = " ".join(str(valor).strip().split())
    texto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in texto if not unicodedata.combining(c)).casefold()

df_raw = pd.DataFrame(dados_aplicacao[3:])
colunas_validas = [i for i in MAPEAMENTO_COLUNAS.keys() if i < df_raw.shape[1]]
df = df_raw.iloc[:, colunas_validas].rename(columns=MAPEAMENTO_COLUNAS)

df = df[df["Colaborador"].astype(str).str.strip() != ""].copy()
df["Nome Normalizado"] = df["Colaborador"].apply(normalizar_texto)

df["Data Monitoria"] = pd.to_datetime(
    df["Data Monitoria"].astype(str).str.strip(),
    format="%d/%m/%Y",
    errors="coerce"
)
df = df.drop_duplicates(subset=["Nome Normalizado"], keep="first").copy()
df["Realizada"] = df["Data Monitoria"].notna()

# =========================================================
# SIDEBAR LATERAL DA IMAGEM
# =========================================================

with st.sidebar:
    st.markdown('<div class="sidebar-title">DASHBOARD</div>', unsafe_allow_html=True)
    
    st.markdown('🔍 **Search...**')
    st.divider()

    secao = st.radio(
        "Navegação",
        ["Home", "Charts", "Favorites", "Chat", "Setting", "Help"],
        label_visibility="collapsed"
    )

    st.markdown('<div class="sidebar-section-title">Development</div>', unsafe_allow_html=True)
    st.markdown("▶ Your Menu 01")
    st.markdown("▶ Your Menu 02")
    st.markdown("▶ Your Menu 03")
    st.markdown("▶ Your Menu 04")
    
    st.divider()
    if st.button("↻ Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# =========================================================
# BARRA DE BUSCA E CABEÇALHO SUPERIOR
# =========================================================

st.markdown(
    """
    <div class="search-bar-container">
        <div class="search-input-fake">
            🔍 &nbsp; Search anything...
        </div>
        <div class="user-profile-fake">
            Hi, John ! &nbsp; 👤
        </div>
    </div>
    <div class="breadcrumb-text">Dashboard > Monitoria Geral</div>
    """,
    unsafe_allow_html=True
)

# =========================================================
# LINHA 1: DETAILED CHART 01 & AVERAGE CHARTS
# =========================================================

col_top_left, col_top_right = st.columns([2.6, 1])

with col_top_left:
    st.markdown('<div class="ui-card"><div class="ui-card-title">Detailed Chart 01</div>', unsafe_allow_html=True)
    
    # Processa histórico mensal de monitorias
    df_dates = df.loc[df["Data Monitoria"].notna(), "Data Monitoria"]
    if not df_dates.empty:
        df_counts = df_dates.groupby(df_dates.dt.to_period("M")).size().reset_index(name="Total")
        df_counts["Mes"] = df_counts["Data Monitoria"].dt.strftime("%b").str.upper()
        x_vals = df_counts["Mes"].tolist()
        y_vals = df_counts["Total"].tolist()
    else:
        x_vals = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG"]
        y_vals = [2500, 3500, 1400, 4000, 4500, 5800, 3600, 4600]

    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=x_vals,
        y=y_vals,
        mode='lines+markers',
        line=dict(color=COLOR_YELLOW, width=3),
        marker=dict(color=COLOR_BLUE, size=8, line=dict(color='white', width=2)),
        hovertemplate='%{x}: %{y}<extra></extra>'
    ))

    fig_line.update_layout(
        height=220,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, tickfont=dict(size=10, color="#94A3B8")),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9", tickfont=dict(size=10, color="#94A3B8")),
        showlegend=False
    )
    st.plotly_chart(fig_line, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

with col_top_right:
    st.markdown('<div class="ui-card"><div class="ui-card-title">Average Charts</div>', unsafe_allow_html=True)
    
    # Gráfico de Barras Horizontais (4 Indicadores)
    categories = ["Chart 01", "Chart 02", "Chart 03", "Chart 04"]
    values = [80, 45, 65, 90]
    bar_colors = [COLOR_RED, COLOR_BLUE, COLOR_YELLOW, COLOR_GREEN]

    fig_avg = go.Figure()
    for cat, val, col in zip(categories, values, bar_colors):
        fig_avg.add_trace(go.Bar(
            y=[cat],
            x=[val],
            orientation='h',
            marker=dict(color=col, cornerradius=4),
            width=0.35,
            hovertemplate='%{y}: %{x}%<extra></extra>'
        ))

    fig_avg.update_layout(
        height=220,
        margin=dict(l=0, r=10, t=10, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, range=[0, 100], showticklabels=False),
        yaxis=dict(showgrid=False, tickfont=dict(size=10, color="#94A3B8")),
        showlegend=False,
        barmode='stack'
    )
    st.plotly_chart(fig_avg, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

st.write("")

# =========================================================
# LINHA 2: TRÊS CARDS DE MÉTRICAS & RECENTLY NEWS (COLUNA DIREITA)
# =========================================================

col_main_body, col_news = st.columns([2.6, 1])

with col_main_body:
    # Métricas Principais
    col_m1, col_m2, col_m3 = st.columns(3)

    total_cols = len(df)
    realizadas = int(df["Realizada"].sum())
    pct_conclusao = (realizadas / total_cols * 100) if total_cols > 0 else 0

    # Funções para gerar minigráficos de onda sob cada métrica
    def criar_sparkline(y_data, color_hex):
        fig = go.Figure(go.Scatter(
            x=list(range(len(y_data))),
            y=y_data,
            fill='tozeroy',
            mode='none',
            fillcolor=color_hex
        ))
        fig.update_layout(
            height=60,
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            showlegend=False
        )
        return fig

    with col_m1:
        st.markdown(
            f"""
            <div class="metric-card-custom">
                <div class="metric-card-title">Earnings</div>
                <div class="metric-card-value" style="color:{COLOR_BLUE};">$ {realizadas*27:.0f}</div>
                <div class="metric-card-sub">*lorem ipsum dolor</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.plotly_chart(criar_sparkline([10, 15, 8, 12, 18, 25, 20], "rgba(30,144,255,0.4)"), use_container_width=True, config={"displayModeBar": False})

    with col_m2:
        st.markdown(
            f"""
            <div class="metric-card-custom">
                <div class="metric-card-title">Downloads</div>
                <div class="metric-card-value" style="color:{COLOR_YELLOW};">{total_cols*18,500:_}</div>
                <div class="metric-card-sub">*lorem ipsum dolor</div>
            </div>
            """.replace("_", ","),
            unsafe_allow_html=True
        )
        st.plotly_chart(criar_sparkline([5, 12, 20, 15, 25, 30, 28], "rgba(255,179,0,0.4)"), use_container_width=True, config={"displayModeBar": False})

    with col_m3:
        st.markdown(
            f"""
            <div class="metric-card-custom">
                <div class="metric-card-title">Favorites</div>
                <div class="metric-card-value" style="color:{COLOR_GREEN};">{int(pct_conclao*2320):_}</div>
                <div class="metric-card-sub">*lorem ipsum dolor</div>
            </div>
            """.replace("_", ","),
            unsafe_allow_html=True
        )
        st.plotly_chart(criar_sparkline([8, 10, 15, 12, 22, 18, 26], "rgba(32,178,170,0.4)"), use_container_width=True, config={"displayModeBar": False})

    st.write("")

    # Sub-linha: Profile Strength (Rosca) e Detailed Chart 02 (Barra Vertical)
    col_sub1, col_sub2 = st.columns([1, 1.8])

    with col_sub1:
        st.markdown('<div class="ui-card"><div class="ui-card-title" style="text-align:center;">Profile Strength</div>', unsafe_allow_html=True)
        
        fig_donut = go.Figure(go.Pie(
            values=[pct_conclusao, 100 - pct_conclusao],
            hole=0.75,
            marker=dict(colors=[COLOR_YELLOW, "#F1F5F9"]),
            textinfo='none',
            hovertemplate='%{value:.1f}%<extra></extra>'
        ))

        fig_donut.update_layout(
            height=160,
            margin=dict(l=10, r=10, t=0, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            annotations=[dict(
                text=f"<b>{pct_conclusao:.0f}%</b>",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=22, color=TEXT_MAIN, family="Inter")
            )]
        )
        st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})
        st.markdown('<div class="metric-card-sub" style="text-align:center;">lorem ipsum dolor</div></div>', unsafe_allow_html=True)

    with col_sub2:
        st.markdown('<div class="ui-card"><div class="ui-card-title">Detailed Chart 02</div>', unsafe_allow_html=True)
        
        col_months = ["JAN", "FEB", "MAR", "APR", "MAY"]
        col_vals = [2200, 5200, 4800, 5800, 6800]
        col_colors = [COLOR_RED, COLOR_BLUE, COLOR_YELLOW, COLOR_GREEN, COLOR_PURPLE]

        fig_bar_vert = go.Figure(go.Bar(
            x=col_months,
            y=col_vals,
            marker=dict(color=col_colors, cornerradius=3),
            width=0.35,
            hovertemplate='%{x}: %{y}<extra></extra>'
        ))

        fig_bar_vert.update_layout(
            height=160,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, tickfont=dict(size=10, color="#94A3B8")),
            yaxis=dict(showgrid=True, gridcolor="#F1F5F9", tickfont=dict(size=10, color="#94A3B8")),
            showlegend=False
        )
        st.plotly_chart(fig_bar_vert, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

with col_news:
    st.markdown(
        """
        <div class="ui-card">
            <div class="ui-card-title">Recently News</div>
            <div class="news-item">
                <div class="news-header">yourwebsite.com <span class="news-time">05:30 AM</span></div>
                <div class="news-desc">Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy.</div>
            </div>
            <div class="news-item">
                <div class="news-header">yourwebsite.com <span class="news-time">06:30 AM</span></div>
                <div class="news-desc">Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy.</div>
            </div>
            <div class="news-item">
                <div class="news-header">yourwebsite.com <span class="news-time">08:30 AM</span></div>
                <div class="news-desc">Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy.</div>
            </div>
            <div class="news-item">
                <div class="news-header">yourwebsite.com <span class="news-time">10:30 AM</span></div>
                <div class="news-desc">Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
