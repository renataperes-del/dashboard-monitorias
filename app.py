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
    page_title="Dashboard de Monitorias", page_icon="📊", layout="wide"
)

# =========================================================
# PALETA DE CORES E ESTILOS CSS
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

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    .stApp {{ background: {BG}; color: {TEXT}; font-family: 'Inter', sans-serif; }}
    .block-container {{ max-width: none; padding: 1.25rem 2rem 3rem; }}
    #MainMenu, footer {{ visibility: hidden; }}
    [data-testid="stHeader"] {{ background: transparent !important; }}

    /* Layout Topbar */
    .topbar {{ display:flex; align-items:center; justify-content:space-between; gap:20px; margin-bottom:18px; }}
    .eyebrow {{ color:{PRIMARY}; font-size:11px; font-weight:800; letter-spacing:.10em; text-transform:uppercase; }}
    .page-title {{ color:{TEXT}; font-size:28px; line-height:1.1; font-weight:800; letter-spacing:-.04em; margin-top:5px; }}
    .page-subtitle {{ color:{SECONDARY}; font-size:12px; margin-top:6px; }}

    /* Cards e Métricas */
    .metric-card {{
        background:{CARD}; border:1px solid {BORDER}; border-radius:13px;
        padding:16px 17px; min-height:105px; box-shadow:0 4px 15px rgba(31,41,55,.035);
    }}
    .metric-label {{ color:{SECONDARY}; font-size:10px; font-weight:800; letter-spacing:.08em; text-transform:uppercase; }}
    .metric-value {{ color:{TEXT}; font-size:27px; font-weight:800; line-height:1; margin-top:11px; font-variant-numeric:tabular-nums; }}
    .metric-foot {{ color:{SECONDARY}; font-size:10px; margin-top:8px; }}

    /* Painéis e Módulos */
    .panel-card {{
        background:{CARD}; border:1px solid {BORDER}; border-radius:14px;
        padding:15px 17px 10px; box-shadow:0 4px 15px rgba(31,41,55,.035); height:100%; box-sizing:border-box;
    }}
    .panel-card-title {{ color:{TEXT}; font-size:13px; font-weight:800; }}
    .panel-card-subtitle {{ color:{SECONDARY}; font-size:10px; margin-top:3px; margin-bottom:4px; }}

    /* Estilos das Listas e Elementos Customizados */
    .praca-card, .team-card, .list-card {{
        background:{CARD}; border:1px solid {BORDER}; border-radius:12px; padding:12px 15px; margin-bottom:10px;
    }}
    .praca-name, .team-name, .list-title {{ font-size:13px; font-weight:700; color:{TEXT}; }}
    .praca-info, .pending-meta {{ font-size:11px; color:{SECONDARY}; margin-top:4px; }}
    .praca-dot {{ height:8px; width:8px; background-color:{PRIMARY}; border-radius:50%; display:inline-block; margin-right:6px; }}
    
    .team-progress {{ background:{BG}; border-radius:6px; height:6px; width:100%; margin:8px 0; overflow:hidden; }}
    .team-progress-fill {{ background:{PRIMARY}; height:100%; border-radius:6px; }}
    .team-status {{ display:flex; justify-content:space-between; font-size:10px; font-weight:600; }}
    .team-realizada {{ color:{SUCCESS}; }}
    .team-pendente {{ color:{WARNING}; }}

    .list-item {{ display:flex; justify-content:space-between; align-items:center; padding:6px 0; border-bottom:1px solid {BORDER}; }}
    .list-item:last-child {{ border-bottom:none; }}
    .list-name {{ font-size:11px; font-weight:600; color:{TEXT}; }}
    .list-function {{ font-size:10px; color:{SECONDARY}; }}
    .list-score {{ font-size:11px; font-weight:700; color:{PRIMARY}; }}
    .empty-message {{ font-size:11px; color:{SECONDARY}; font-style:italic; padding:8px 0; }}

    /* Filtros e Controles */
    .filter-panel {{
        background:{CARD}; border:1px solid {BORDER}; border-radius:14px;
        padding:14px 16px 4px; box-shadow:0 4px 18px rgba(31,41,55,.035); margin-bottom:16px;
    }}
    .filter-summary {{
        background:{PRIMARY_SOFT}; border:1px solid #DCE4FF; border-radius:9px;
        padding:8px 12px; margin:0 0 14px; color:{TEXT}; font-size:10px;
    }}
    .status-list {{ margin-top:4px; }}
    .status-row {{ display:flex; justify-content:space-between; align-items:center; padding:9px 0; border-bottom:1px solid {BORDER}; font-size:11px; }}
    .status-row:last-child {{ border-bottom:0; }}
    .status-name {{ color:{SECONDARY}; }}
    .status-number {{ color:{TEXT}; font-weight:800; }}

    /* Botões Streamlit */
    .stButton > button {{ border:1px solid {BORDER}; border-radius:9px; background:{CARD}; color:{TEXT}; font-weight:700; min-height:40px; }}
    .stButton > button:hover {{ border-color:{PRIMARY}; color:{PRIMARY}; }}
    .stDownloadButton > button {{ border:1px solid {BORDER}; border-radius:9px; background:{CARD}; font-size:11px; }}
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# CONEXÃO GOOGLE SHEETS
# =========================================================

SHEET_ID = "1bSYqD9wLkpMxTIGN6kyFh6zuVTixM384oQr8cGskYcM"
ABA = "Aplicação"


@st.cache_resource
def get_client():
    credenciais = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
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
            "Erro ao conectar com o Google Sheets. "
            "Verifique os segredos da Service Account ou a internet."
        ) from erro


try:
    dados_aplicacao, data_consulta = carregar_dados()
except RuntimeError as erro:
    st.error(str(erro))
    st.stop()

if len(dados_aplicacao) <= 3:
    st.error("A aba 'Aplicação' não possui dados suficientes.")
    st.stop()


# =========================================================
# TRATAMENTO E ESTRUTURA DOS DADOS
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
    12: "Observações Gerais",
}


def normalizar_texto(valor):
    if pd.isna(valor):
        return ""
    texto = " ".join(str(valor).strip().split())
    texto = unicodedata.normalize("NFKD", texto)
    return "".join(
        c for c in texto if not unicodedata.combining(c)
    ).casefold()


def primeiro_nome(valor):
    texto = normalizar_texto(valor)
    return texto.split()[0] if texto else ""


# Construção direta do DataFrame (otimizado em C/Pandas)
df_raw = pd.DataFrame(dados_aplicacao[3:])
colunas_presentes = [i for i in MAPEAMENTO_COLUNAS.keys() if i < df_raw.shape[1]]
monitorias_google = df_raw.iloc[:, colunas_presentes].rename(
    columns=MAPEAMENTO_COLUNAS
)
monitorias_google["_Linha Planilha"] = range(4, 4 + len(monitorias_google))

# Limpeza e filtros básicos
monitorias_google = monitorias_google[
    monitorias_google["Colaborador"].astype(str).str.strip() != ""
].copy()
monitorias_google["Colaborador"] = (
    monitorias_google["Colaborador"].astype(str).str.strip()
)
monitorias_google["Supervisão"] = (
    monitorias_google["Supervisão"].astype(str).str.strip()
)
monitorias_google["Nome Normalizado"] = monitorias_google["Colaborador"].apply(
    normalizar_texto
)

# Parsing Seguro de Datas
COLUNAS_DATA = ["Data Monitoria", "Data Lado a Lado", "Data Monitoria Offline"]
datas_invalidas = {}

for coluna in COLUNAS_DATA:
    texto_original = monitorias_google[coluna].astype(str).str.strip()
    preenchidas = texto_original.notna() & (
        ~texto_original.isin(["", "nan", "<NA>"])
    )
    convertida = pd.to_datetime(
        texto_original, format="%d/%m/%Y", errors="coerce"
    )

    falhas = preenchidas & convertida.isna()
    if falhas.any():
        datas_invalidas[coluna] = monitorias_google.loc[
            falhas, ["Colaborador", coluna, "_Linha Planilha"]
        ].copy()

    monitorias_google[coluna] = convertida

if datas_invalidas:
    total_invalidas = sum(len(df) for df in datas_invalidas.values())
    with st.expander(
        f"⚠️ {total_invalidas} data(s) fora do formato padrão (dd/mm/aaaa)"
    ):
        for coluna, df_inv in datas_invalidas.items():
            st.markdown(f"**{coluna}:**")
            for _, lin in df_inv.iterrows():
                st.write(
                    f"- Linha {int(lin['_Linha Planilha'])}: {lin['Colaborador']} ({lin[coluna]})"
                )

# Deduplicação mantendo primeira entrada
monitorias_google = monitorias_google.drop_duplicates(
    subset=["Nome Normalizado"], keep="first"
).copy()
monitorias_google["Realizada"] = monitorias_google["Data Monitoria"].notna()


# =========================================================
# FUNÇÕES E NOTAS DOS COLABORADORES
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
    "Keren Jamille Coutinho Albrechete",
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
    "Stella Angela da Silva",
]

funcao_map = {normalizar_texto(n): "Exec" for n in execs}
funcao_map.update({normalizar_texto(n): "Apoio ADM" for n in apoio_adm})

monitorias_google["Função"] = (
    monitorias_google["Nome Normalizado"]
    .map(funcao_map)
    .fillna("Não identificado")
)

# Mapeamento de Notas Exemplo
notas_monitoria = {
    "Pedro Llanos Iampietro": [75.26, 76.46],
    "Matheus Lacerda Lima": [94.00, 77.66],
    "Gabriel Soares Gonçalves": [80.73, 80.66],
    "Laura Marques da Silva": [75.86, 81.93],
    "Felipe Santos Nery": [77.66, 75.86],
    "Evellyn Silva dos Santos": [86.20, 81.22],
}

notas_norm = {normalizar_texto(k): v for k, v in notas_monitoria.items()}
monitorias_google["Média"] = monitorias_google["Nome Normalizado"].apply(
    lambda x: (sum(notas_norm[x]) / len(notas_norm[x]))
    if x in notas_norm and len(notas_norm[x]) > 0
    else None
)


# =========================================================
# MAPEAMENTO DE PRAÇAS E SUPERVISÕES
# =========================================================

pracas = {
    "São Paulo": {
        "responsavel": "Danielly Palaro",
        "supervisores": [
            "Wesley Alves Martins",
            "Kelly Gonzaga Querido",
            "Jean Cássio Negri dos Santos",
            "Julio César Castro",
            "Murilo Henrique Xavier",
        ],
    },
    "GMSP": {
        "responsavel": "Caio Marques",
        "supervisores": [
            "Camila Dias Silva",
            "Laila Cerqueira Rodrigues",
            "Alexssander Affonso da Silva",
        ],
    },
    "Conne-Sul": {
        "responsavel": "Evelyn Viegas",
        "supervisores": [
            "Angelica Yumi Gaspar de Oliveira",
            "Karine Conceição Rodrigues",
        ],
    },
    "Sudeste": {
        "responsavel": "Darlene Carvalho",
        "supervisores": ["Maiara Bravo", "Letícia da Silva Santos"],
    },
}

supervisao_canonica_por_primeiro_nome = {}
praca_por_primeiro_nome = {}

for nome_praca, dados in pracas.items():
    for sup in dados["supervisores"]:
        p_normalizado = primeiro_nome(sup)
        p_original = str(sup).strip().split()[0]
        supervisao_canonica_por_primeiro_nome[p_normalizado] = p_original
        praca_por_primeiro_nome[p_normalizado] = nome_praca

monitorias_google["Praça"] = monitorias_google["Supervisão"].apply(
    lambda s: praca_por_primeiro_nome.get(primeiro_nome(s), "Outros")
)


# =========================================================
# NAUFRÁGIO / INTERFACE PRINCIPAL
# =========================================================

st.sidebar.markdown("### NUBE")
st.sidebar.caption("Treinamento Comercial")
st.sidebar.markdown("**Monitorias**")
nav_secao = st.sidebar.radio(
    "",
    [
        "Visão geral",
        "Indicadores",
        "Supervisores",
        "Pendências",
        "Evolução",
        "Etapas",
    ],
    label_visibility="collapsed",
)
st.sidebar.divider()
st.sidebar.caption("Painel de acompanhamento das monitorias")

# Header Principal
col_header, col_update = st.columns([5, 1])
with col_header:
    st.html(
        """
        <div class="topbar">
            <div>
                <div class="eyebrow">Nube • Treinamento Comercial</div>
                <div class="page-title">Dashboard de Monitorias</div>
                <div class="page-subtitle">Acompanhamento das aplicações e evolução das equipes</div>
            </div>
        </div>
        """
    )

with col_update:
    st.write("")
    if st.button("↻ Atualizar", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.caption(f"Atualizado em {data_consulta}")


# =========================================================
# FILTROS
# =========================================================

st.html(
    """
    <div class="filter-panel">
        <div class="panel-title">Filtros</div>
        <div class="panel-subtitle">Use os filtros para atualizar todos os indicadores e gráficos.</div>
    </div>
    """
)

col_f_praca, col_f_sup, col_f_status = st.columns(3)

with col_f_praca:
    praca_selecionada = st.selectbox("Praça", ["Todas"] + list(pracas.keys()))

# Filtragem dinâmica de supervisões
if praca_selecionada == "Todas":
    sups_disp = sorted(
        {
            supervisao_canonica_por_primeiro_nome.get(
                primeiro_nome(s), str(s).strip().split()[0]
            )
            for s in monitorias_google["Supervisão"].dropna().astype(str)
            if primeiro_nome(s)
        },
        key=normalizar_texto,
    )
else:
    sups_praca = {
        primeiro_nome(s) for s in pracas[praca_selecionada]["supervisores"]
    }
    sups_disp = sorted(
        {
            supervisao_canonica_por_primeiro_nome.get(
                primeiro_nome(s), str(s).strip().split()[0]
            )
            for s in monitorias_google["Supervisão"].dropna().astype(str)
            if primeiro_nome(s) in sups_praca
        },
        key=normalizar_texto,
    )

with col_f_sup:
    supervisao_selecionada = st.selectbox("Supervisão", ["Todas"] + sups_disp)

with col_f_status:
    status_selecionado = st.selectbox(
        "Status", ["Todos", "Realizadas", "Pendentes"]
    )

# Aplicação do Filtro no DataFrame
df_ativo = monitorias_google.copy()

if praca_selecionada != "Todas":
    df_ativo = df_ativo[df_ativo["Praça"] == praca_selecionada]

if supervisao_selecionada != "Todas":
    df_ativo = df_ativo[
        df_ativo["Supervisão"].astype(str).map(normalizar_texto)
        == normalizar_texto(supervisao_selecionada)
    ]

if status_selecionado == "Realizadas":
    df_ativo = df_ativo[df_ativo["Realizada"]]
elif status_selecionado == "Pendentes":
    df_ativo = df_ativo[~df_ativo["Realizada"]]


# =========================================================
# INDICADORES DA PASTA (CARDS DE TOPO)
# =========================================================

total_colaboradores = len(df_ativo)
total_realizadas = int(df_ativo["Realizada"].sum())
total_pendentes = total_colaboradores - total_realizadas
percentual_concluido = (
    (total_realizadas / total_colaboradores * 100) if total_colaboradores else 0
)
notas_validas = df_ativo.loc[df_ativo["Média"].notna(), "Média"]
media_geral = notas_validas.mean() if not notas_validas.empty else None

c1, c2, c3, c4, c5 = st.columns(5)
metrics = [
    ("COLABORADORES", total_colaboradores, "no acompanhamento"),
    ("REALIZADAS", total_realizadas, "monitorias concluídas"),
    ("PENDENTES", total_pendentes, "monitorias a realizar"),
    ("CONCLUSÃO", f"{percentual_concluido:.1f}%", "do total"),
    (
        "MÉDIA",
        f"{media_geral:.1f}%" if media_geral is not None else "—",
        "notas registradas",
    ),
]

for col, (tit, val, sub) in zip([c1, c2, c3, c4, c5], metrics):
    with col:
        st.html(
            f"""
            <div class="metric-card">
                <div class="metric-label">{tit}</div>
                <div class="metric-value">{val}</div>
                <div class="metric-foot">{sub}</div>
            </div>
            """
        )


# =========================================================
# GRÁFICOS
# =========================================================

st.write("")
col_evolucao, col_status = st.columns([2.1, 1])

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
    "Dez",
]

with col_evolucao:
    st.html(
        """
        <div class="panel-card">
            <div class="panel-card-title">Evolução das monitorias</div>
            <div class="panel-card-subtitle">Quantidade de monitorias realizadas por mês</div>
        </div>
        """
    )

    datas_v = df_ativo.loc[df_ativo["Data Monitoria"].notna(), "Data Monitoria"]
    agora_no_tz = datetime.now(ZoneInfo("America/Sao_Paulo")).replace(
        tzinfo=None
    )

    if not datas_v.empty:
        p_min = datas_v.min().to_period("M")
        p_max = max(datas_v.max().to_period("M"), pd.Period(agora_no_tz, "M"))
        range_meses = pd.period_range(p_min, p_max, freq="M")
    else:
        range_meses = pd.period_range(
            pd.Period(agora_no_tz, "M"), pd.Period(agora_no_tz, "M"), freq="M"
        )

    eixo_x, eixo_y = [], []
    for p in range_meses:
        qtd = df_ativo[
            (df_ativo["Data Monitoria"] >= p.start_time)
            & (df_ativo["Data Monitoria"] <= p.end_time)
        ].shape[0]
        eixo_x.append(f"{MESES[p.month - 1]}/{str(p.year)[2:]}")
        eixo_y.append(qtd)

    fig_evo = go.Figure(
        go.Scatter(
            x=eixo_x,
            y=eixo_y,
            mode="lines+markers",
            line=dict(color=PRIMARY, width=3),
            marker=dict(color=PRIMARY, size=7),
            hovertemplate="%{x}: %{y} monitorias<extra></extra>",
        )
    )
    fig_evo.update_layout(
        height=270,
        margin=dict(l=8, r=8, t=12, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=TEXT),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor=BORDER, zeroline=False),
        showlegend=False,
    )
    st.plotly_chart(
        fig_evo, use_container_width=True, config={"displayModeBar": False}
    )

with col_status:
    st.html(
        """
        <div class="panel-card">
            <div class="panel-card-title">Status das monitorias</div>
            <div class="panel-card-subtitle">Distribuição do acompanhamento atual</div>
        </div>
        """
    )

    fig_st = go.Figure(
        go.Pie(
            values=[total_realizadas, total_pendentes],
            labels=["Realizadas", "Pendentes"],
            hole=0.70,
            marker=dict(colors=[SUCCESS, WARNING]),
            textinfo="none",
            hovertemplate="%{label}: %{value}<extra></extra>",
        )
    )
    fig_st.update_layout(
        height=220,
        margin=dict(l=8, r=8, t=8, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        annotations=[
            dict(
                text=f"<b>{percentual_concluido:.0f}%</b><br><span style='font-size:10px'>concluído</span>",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=22, color=TEXT),
            )
        ],
    )
    st.plotly_chart(
        fig_st, use_container_width=True, config={"displayModeBar": False}
    )


# =========================================================
# DETALHES E PENDÊNCIAS
# =========================================================

st.write("")
col_pend, col_etapas = st.columns([1.7, 1])

with col_pend:
    st.html(
        """
        <div class="panel-card">
            <div class="panel-card-title">Pendências</div>
            <div class="panel-card-subtitle">Colaboradores aguardando monitoria</div>
        </div>
        """
    )
    pendencias = df_ativo[~df_ativo["Realizada"]].sort_values(
        ["Supervisão", "Colaborador"]
    )

    if pendencias.empty:
        st.info("Nenhuma pendência encontrada para os filtros selecionados.")
    else:
        st.dataframe(
            pendencias[["Colaborador", "Função", "Supervisão", "Praça"]],
            use_container_width=True,
            hide_index=True,
        )
        st.download_button(
            "Baixar Pendências em CSV",
            data=pendencias[["Colaborador", "Função", "Supervisão", "Praça"]]
            .to_csv(index=False)
            .encode("utf-8-sig"),
            file_name="pendencias_monitoria.csv",
            mime="text/csv",
        )

with col_etapas:
    t_lado = int(df_ativo["Data Lado a Lado"].notna().sum())
    t_off = int(df_ativo["Data Monitoria Offline"].notna().sum())

    st.html(
        f"""
        <div class="panel-card">
            <div class="panel-card-title">Outras etapas</div>
            <div class="panel-card-subtitle">Acompanhamento complementar</div>
            <div class="status-list" style="margin-top:12px;">
                <div class="status-row"><span class="status-name">Lado a lado</span><span class="status-number">{t_lado}</span></div>
                <div class="status-row"><span class="status-name">Monitoria offline</span><span class="status-number">{t_off}</span></div>
            </div>
        </div>
        """
    )
