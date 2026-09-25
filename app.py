import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import gspread
import html
import unicodedata
import hmac
import hashlib
import secrets

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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {{
        --bg: {BG};
        --card: {CARD};
        --border: {BORDER};
        --text: {TEXT};
        --secondary: {SECONDARY};
        --primary: {PRIMARY};
    }}

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}

    .stApp {{
        background: {BG};
        color: {TEXT};
    }}

    /* Esconde o chrome padrão do Streamlit sem mexer no conteúdo */
    #MainMenu, footer, [data-testid="stToolbar"] {{
        visibility: hidden;
    }}

    [data-testid="stHeader"] {{
        background: transparent !important;
    }}

    /* Área principal alinhada ao modelo do dashboard */
    .block-container {{
        width: calc(100vw - 260px);
        max-width: none;
        margin-left: 230px;
        margin-right: 0;
        padding: 28px 48px 56px 32px;
        box-sizing: border-box;
    }}

    /* =====================================================
       SIDEBAR
       ===================================================== */

    .sidebar {{
        position: fixed;
        z-index: 999999;
        left: 0;
        top: 0;
        bottom: 0;
        width: 230px;
        padding: 30px 16px 22px;
        background: linear-gradient(180deg, #607EAF 0%, #5A78A8 100%);
        color: white;
        box-sizing: border-box;
        box-shadow: 6px 0 24px rgba(35, 53, 82, .08);
    }}

    .sidebar-brand {{
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 0 8px 34px;
    }}

    .sidebar-logo {{
        width: 36px;
        height: 36px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(255,255,255,.17);
        border: 1px solid rgba(255,255,255,.10);
        font-weight: 800;
        font-size: 15px;
    }}

    .sidebar-title {{
        font-size: 12px;
        font-weight: 800;
        letter-spacing: .07em;
    }}

    .nav-label {{
        color: rgba(255,255,255,.58);
        font-size: 10px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: .12em;
        padding: 0 10px 8px;
        margin-top: 5px;
    }}

    .nav-item {{
        display: flex;
        align-items: center;
        gap: 11px;
        padding: 11px 10px;
        margin: 3px 0;
        border-radius: 9px;
        color: rgba(255,255,255,.88);
        font-size: 12px;
        font-weight: 500;
        transition: background .15s ease, transform .15s ease;
    }}

    .nav-item:hover {{
        background: rgba(255,255,255,.09);
    }}

    .nav-item.active {{
        background: rgba(255,255,255,.18);
        color: #fff;
        font-weight: 700;
        box-shadow: inset 0 0 0 1px rgba(255,255,255,.04);
    }}

    .nav-icon {{
        width: 17px;
        text-align: center;
        font-size: 13px;
        opacity: .95;
    }}

    .sidebar-note {{
        position: absolute;
        left: 16px;
        right: 16px;
        bottom: 22px;
        padding: 12px 12px;
        border: 1px solid rgba(255,255,255,.13);
        border-radius: 10px;
        background: rgba(255,255,255,.07);
        color: rgba(255,255,255,.68);
        font-size: 10px;
        line-height: 1.5;
    }}

    /* =====================================================
       CABEÇALHO
       ===================================================== */

    .topbar {{
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 24px;
        margin-bottom: 26px;
    }}

    .eyebrow {{
        color: {PRIMARY};
        font-size: 12px;
        font-weight: 800;
        letter-spacing: .10em;
        text-transform: uppercase;
    }}

    .page-title {{
        color: {TEXT};
        font-size: 44px;
        line-height: 1.08;
        font-weight: 800;
        letter-spacing: -.045em;
        margin-top: 6px;
    }}

    .page-subtitle {{
        color: {SECONDARY};
        font-size: 16px;
        margin-top: 8px;
    }}

    .update-info {{
        color: {SECONDARY};
        font-size: 10px;
        text-align: right;
        margin-top: 8px;
    }}

    /* =====================================================
       FILTROS
       ===================================================== */

    .filter-panel {{
        background: {CARD};
        border: 1px solid {BORDER};
        border-radius: 15px;
        padding: 17px 18px 8px;
        box-shadow: 0 5px 20px rgba(31,41,55,.035);
        margin-bottom: 14px;
    }}

    .panel-title {{
        color: {TEXT};
        font-size: 13px;
        font-weight: 800;
        letter-spacing: -.01em;
        margin-bottom: 4px;
    }}

    .panel-subtitle {{
        color: {SECONDARY};
        font-size: 10px;
        margin-bottom: 8px;
    }}

    label[data-testid="stWidgetLabel"] p {{
        color: #374151 !important;
        font-size: 11px !important;
        font-weight: 600 !important;
    }}

    div[data-baseweb="select"] > div {{
        background: {CARD};
        border: 1px solid #E0E4EC;
        border-radius: 9px;
        min-height: 42px;
        box-shadow: none;
    }}

    div[data-baseweb="select"] > div:hover {{
        border-color: #AFC0EE;
        box-shadow: 0 0 0 3px rgba(67,97,238,.06);
    }}

    div[data-baseweb="select"] [data-baseweb="select-value"] {{
        font-size: 12px;
    }}

    .filter-summary {{
        background: {PRIMARY_SOFT};
        border: 1px solid #DCE4FF;
        border-radius: 9px;
        padding: 9px 12px;
        margin: 0 0 14px;
        color: {TEXT};
        font-size: 10px;
    }}

    /* =====================================================
       CARDS DE MÉTRICAS
       ===================================================== */

    .metric-card {{
        background: {CARD};
        border: 1px solid {BORDER};
        border-radius: 14px;
        padding: 17px 18px;
        min-height: 104px;
        box-shadow: 0 5px 18px rgba(31,41,55,.035);
        box-sizing: border-box;
    }}

    .metric-label {{
        color: #697386;
        font-size: 10px;
        font-weight: 800;
        letter-spacing: .08em;
        text-transform: uppercase;
    }}

    .metric-value {{
        color: {TEXT};
        font-size: 29px;
        font-weight: 800;
        line-height: 1;
        margin-top: 12px;
        letter-spacing: -.035em;
        font-variant-numeric: tabular-nums;
    }}

    .metric-foot {{
        color: #7B8494;
        font-size: 10px;
        margin-top: 8px;
    }}

    /* =====================================================
       PAINÉIS / GRÁFICOS
       ===================================================== */

    .panel-card {{
        background: {CARD};
        border: 1px solid {BORDER};
        border-radius: 15px;
        padding: 16px 18px 10px;
        box-shadow: 0 5px 18px rgba(31,41,55,.035);
        height: 100%;
        box-sizing: border-box;
    }}

    .panel-card-title {{
        color: {TEXT};
        font-size: 13px;
        font-weight: 800;
        letter-spacing: -.01em;
    }}

    .panel-card-subtitle {{
        color: {SECONDARY};
        font-size: 10px;
        margin-top: 4px;
        margin-bottom: 4px;
    }}

    .status-list {{
        margin-top: 5px;
    }}

    .status-row {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 9px 0;
        border-bottom: 1px solid {BORDER};
        font-size: 11px;
    }}

    .status-row:last-child {{
        border-bottom: 0;
    }}

    .status-name {{
        color: {SECONDARY};
    }}

    .status-number {{
        color: {TEXT};
        font-weight: 800;
        font-variant-numeric: tabular-nums;
    }}

    #visao-geral,
    #indicadores,
    #supervisores,
    #pendencias,
    #evolucao,
    #etapas {{
        scroll-margin-top: 24px;
    }}

    /* =====================================================
       BOTÕES / TABELAS / EXPANDERS
       ===================================================== */

    .stButton > button,
    .stDownloadButton > button {{
        border: 1px solid {BORDER};
        border-radius: 9px;
        background: {CARD};
        color: {TEXT};
        font-weight: 700;
        min-height: 40px;
        transition: all .15s ease;
    }}

    .stButton > button:hover,
    .stDownloadButton > button:hover {{
        border-color: #AFC0EE;
        color: {PRIMARY};
        box-shadow: 0 4px 12px rgba(67,97,238,.08);
    }}

    [data-testid="stDataFrame"] {{
        border: 1px solid {BORDER};
        border-radius: 12px;
        overflow: hidden;
    }}

    [data-testid="stExpander"] {{
        border: 1px solid {BORDER};
        border-radius: 11px;
        background: {CARD};
    }}

    /* =====================================================
       RESPONSIVO
       ===================================================== */

    @media (max-width: 1100px) {{
        .block-container {{
            width: 100%;
            margin-left: 0;
            padding: 24px 24px 40px;
        }}

        .sidebar {{
            display: none;
        }}
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# GOOGLE SHEETS / ACESSOS
# =========================================================

SHEET_ID = "1bSYqD9wLkpMxTIGN6kyFh6zuVTixM384oQr8cGskYcM"
ABA = "Aplicação"
ABA_LOG = "Log_Acessos"


@st.cache_resource
def get_client():

    credenciais = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets"
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
# CONTROLE DE ACESSO
# =========================================================

USUARIOS_SUPERVISORES = {
    "julio": "Júlio Castro",
    "jean": "Jean Santos",
    "wesley": "Wesley Martins",
    "kelly": "Kelly Querido",
    "murilo": "Murilo Henrique",
    "alexssander": "Alexssander Silva",
    "laila": "Laila Rodrigues",
    "camila": "Camila Dias",
    "maiara": "Maiara Bravo",
    "leticia": "Leticia Santos",
    "karine": "Karine Rodrigues",
    "angelica": "Angélica Oliveira",
}

USUARIOS_GERENTES = {
    "danielly": "Danielly Palaro",
    "caio": "Caio Marques",
    "darlene": "Darlene Carvalho",
    "evelyn": "Evelyn Viegas",
}

usuarios_secrets = st.secrets.get("usuarios", {})
senhas_supervisores = usuarios_secrets.get("supervisores", {})
senhas_gerentes = usuarios_secrets.get("gerentes", {})
senha_treinamento = usuarios_secrets.get("treinamento", "")

if "usuario_logado" not in st.session_state:
    st.session_state["usuario_logado"] = None
    st.session_state["perfil_acesso"] = None
    st.session_state["nome_acesso"] = None
    st.session_state["supervisao_acesso"] = None

if not st.session_state["usuario_logado"]:

    st.markdown(
        """
        <style>
        .block-container {
            width: 100vw !important;
            max-width: none !important;
            margin-left: 0 !important;
            margin-right: 0 !important;
            padding: 0 48px 40px !important;
            box-sizing: border-box !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div style="text-align:center; margin:0 auto 22px; padding-top:18vh;">
            <div style="font-size:11px;font-weight:800;letter-spacing:.10em;color:#4361EE;text-transform:uppercase;">
                Nube • Treinamento Comercial
            </div>
            <div style="font-size:30px;font-weight:800;color:#1F2937;margin-top:8px;">
                Dashboard de Monitorias
            </div>
            <div style="font-size:12px;color:#6B7280;margin-top:7px;">
                Acesso restrito
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col_login_esq, col_login, col_login_dir = st.columns([1.3, 1, 1.3])

    with col_login:

        with st.form("form_login"):

            usuario_digitado = st.text_input("Usuário").strip().casefold()
            senha_digitada = st.text_input("Senha", type="password")

            entrar = st.form_submit_button(
                "Entrar",
                use_container_width=True
            )

        if entrar:

            perfil = None
            nome = None
            supervisao = None
            senha_valida = False

            if usuario_digitado == "treinamento" and senha_treinamento:

                perfil = "treinamento"
                nome = "Treinamento Comercial"
                senha_valida = hmac.compare_digest(
                    str(senha_digitada),
                    str(senha_treinamento)
                )

            elif usuario_digitado in USUARIOS_SUPERVISORES:

                perfil = "supervisor"
                nome = USUARIOS_SUPERVISORES[usuario_digitado]
                senha_provisoria = senhas_supervisores.get(usuario_digitado)

                senha_valida = (
                    senha_provisoria is not None
                    and hmac.compare_digest(
                        str(senha_digitada),
                        str(senha_provisoria)
                    )
                )

            elif usuario_digitado in USUARIOS_GERENTES:

                perfil = "gerente"
                nome = USUARIOS_GERENTES[usuario_digitado]
                senha_provisoria = senhas_gerentes.get(usuario_digitado)

                senha_valida = (
                    senha_provisoria is not None
                    and hmac.compare_digest(
                        str(senha_digitada),
                        str(senha_provisoria)
                    )
                )

            if senha_valida and perfil in {"supervisor", "gerente", "treinamento"}:

                if perfil == "supervisor":
                    supervisao = usuario_digitado

                st.session_state["usuario_logado"] = usuario_digitado
                st.session_state["perfil_acesso"] = perfil
                st.session_state["nome_acesso"] = nome
                st.session_state["supervisao_acesso"] = supervisao

                registrar_acesso(usuario_digitado, perfil, nome)

                st.rerun()

            else:
                st.error("Usuário ou senha inválidos.")

    st.stop()


PERFIL_ACESSO = st.session_state["perfil_acesso"]
NOME_ACESSO = st.session_state["nome_acesso"]
SUPERVISAO_ACESSO = st.session_state["supervisao_acesso"]


# =========================================================
# CARREGAMENTO
# =========================================================

# =========================================================

try:

    dados_aplicacao, data_consulta = carregar_dados()

except RuntimeError as erro:

    st.error(str(erro))
    st.stop()


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
    "Colaborador", "Supervisão", "Data Monitoria", "Quem Aplicou Monitoria",
    "Ligação 1", "Ligação 2", "Data Lado a Lado", "Quem Aplicou Lado a Lado",
    "Observação Lado a Lado", "Data Monitoria Offline", "Quem Aplicou Offline",
    "Percentual Offline", "Observações Gerais"
]

# A aba possui 3 linhas de cabeçalho. Os dados começam na linha 4.
# Mantemos o mapeamento posicional para não confundir os cabeçalhos
# de Monitoria, Lado a Lado e Monitoria Offline.
linhas_dados = []
for numero_planilha, linha in enumerate(dados_aplicacao[3:], start=4):
    linha = list(linha)
    if len(linha) < len(COLUNAS_ESPERADAS):
        linha = linha + [""] * (len(COLUNAS_ESPERADAS) - len(linha))
    registro = {
        coluna: linha[indice]
        for indice, coluna in enumerate(COLUNAS_ESPERADAS)
    }
    registro["_Linha Planilha"] = numero_planilha
    linhas_dados.append(registro)

if not linhas_dados:
    st.error("Não foram encontradas linhas de colaboradores na aba 'Aplicação'.")
    st.stop()

monitorias_google = pd.DataFrame(linhas_dados)

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


# Supervisor visualiza exclusivamente os registros da própria equipe.
# O filtro é aplicado no dataframe base, antes dos indicadores, gráficos e tabelas.
if PERFIL_ACESSO == "supervisor":
    supervisao_alvo = normalizar_texto(SUPERVISAO_ACESSO)
    monitorias_google = monitorias_google[
        monitorias_google["Supervisão"].astype(str).map(primeiro_nome)
        == supervisao_alvo
    ].copy()

    if monitorias_google.empty:
        st.error(
            f"Nenhum registro encontrado para a supervisão de {NOME_ACESSO}. "
            "Verifique o nome da supervisão na aba 'Aplicação'."
        )
        st.stop()


monitorias_google["Nome Normalizado"] = monitorias_google["Colaborador"].apply(normalizar_texto)


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

        datas_invalidas[coluna] = monitorias_google.loc[falhas, ["Colaborador", coluna, "_Linha Planilha"]].copy()

    monitorias_google[coluna] = convertida


if datas_invalidas:

    quantidade_datas_invalidas = sum(
        len(linhas)
        for linhas in datas_invalidas.values()
    )

    st.warning(
        f"⚠️ Foram encontradas {quantidade_datas_invalidas} "
        "data(s) fora do formato esperado (dd/mm/aaaa). "
        "Essas datas não foram consideradas como monitorias realizadas."
    )

    with st.expander("Ver colaboradores com data inválida"):

        for coluna, linhas_invalidas in datas_invalidas.items():
            st.markdown(f"**{coluna}:**")
            for _, linha in linhas_invalidas.iterrows():
                st.write(f"- Linha {int(linha['_Linha Planilha'])}: {linha['Colaborador']} | valor: {linha[coluna]}")


# =========================================================
# DUPLICIDADES
# =========================================================

duplicados = (
    monitorias_google
    .groupby("Nome Normalizado")
    .agg(
        Colaborador=("Colaborador", "first"),
        Registros=("Colaborador", "size")
    )
    .query("Registros > 1")
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

        for _, linha in duplicados.iterrows():
            st.write(f"- {linha['Colaborador']}: {int(linha['Registros'])} registros")


# Mantém apenas um registro por colaborador normalizado.
# Se houver duplicidade, ela é sinalizada acima para correção na origem.
monitorias_google = monitorias_google.drop_duplicates(
    subset=["Nome Normalizado"], keep="first"
).copy()


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

# Usa os nomes cadastrados em `pracas` como padrão de exibição.
# Assim, diferenças como "Júlio" e "Julio" na planilha
# não criam duas opções diferentes no dashboard.
supervisao_canonica_por_primeiro_nome = {}

for dados_praca in pracas.values():

    for supervisor in dados_praca["supervisores"]:

        primeiro_original = str(supervisor).strip().split()[0]
        primeiro_normalizado = primeiro_nome(supervisor)

        supervisao_canonica_por_primeiro_nome[
            primeiro_normalizado
        ] = primeiro_original


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
# INTERFACE DA DASHBOARD
# =========================================================

st.html(
    """
    <aside class="sidebar">
        <div class="sidebar-brand">
            <div class="sidebar-logo">N</div>
            <div class="sidebar-title">DASHBOARD</div>
        </div>
        <div class="nav-label">Monitorias</div>
        <a class="nav-item active" href="#visao-geral"><span class="nav-icon">⌂</span> Visão geral</a>
        <a class="nav-item" href="#indicadores"><span class="nav-icon">▥</span> Indicadores</a>
        <a class="nav-item" href="#supervisores"><span class="nav-icon">●</span> Supervisores</a>
        <a class="nav-item" href="#pendencias"><span class="nav-icon">☷</span> Pendências</a>
        <div class="nav-label" style="margin-top:20px;">Acompanhamento</div>
        <a class="nav-item" href="#evolucao"><span class="nav-icon">◷</span> Evolução</a>
        <a class="nav-item" href="#etapas"><span class="nav-icon">✓</span> Etapas</a>
        <div class="sidebar-note">
            Nube • Treinamento Comercial<br>
            Painel de acompanhamento das monitorias
        </div>
    </aside>
    """
)

col_header, col_update, col_sair = st.columns([5, 0.85, 0.65])
with col_header:
    st.html(
        f"""<div class="topbar">
            <div>
                <div class="eyebrow">Nube • Treinamento Comercial</div>
                <div class="page-title">Dashboard de Monitorias</div>
                <div class="page-subtitle">Acompanhamento das aplicações e evolução das equipes</div>
                <div style="color:#4361EE;font-size:15px;font-weight:700;margin-top:11px;">Olá, {html.escape(primeiro_nome(NOME_ACESSO).title())}!</div>
            </div>
        </div>"""
    )

with col_update:
    st.write("")
    if st.button("↻ Atualizar", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.html(f'<div class="update-info">Atualizado em {data_consulta}</div>')

with col_sair:
    st.write("")
    if st.button("Sair", use_container_width=True):
        st.session_state["usuario_logado"] = None
        st.session_state["perfil_acesso"] = None
        st.session_state["nome_acesso"] = None
        st.session_state["supervisao_acesso"] = None
        st.rerun()


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

col_filtro_praca, col_filtro_supervisao, col_filtro_status = st.columns(3)

opcoes_praca = ["Todas"] + list(pracas.keys())

with col_filtro_praca:
    praca_selecionada = st.selectbox("Praça", opcoes_praca)

if praca_selecionada == "Todas":
    supervisoes_disponiveis = sorted(
        {
            supervisao_canonica_por_primeiro_nome.get(
                primeiro_nome(supervisao),
                str(supervisao).strip().split()[0]
            )
            for supervisao in monitorias_google["Supervisão"].dropna().astype(str).tolist()
            if primeiro_nome(supervisao)
        },
        key=normalizar_texto
    )
else:
    supervisoes_da_praca = {
        primeiro_nome(nome)
        for nome in pracas[praca_selecionada]["supervisores"]
    }
    supervisoes_disponiveis = sorted(
        {
            supervisao_canonica_por_primeiro_nome.get(
                primeiro_nome(supervisao),
                str(supervisao).strip().split()[0]
            )
            for supervisao in monitorias_google["Supervisão"].dropna().astype(str).tolist()
            if primeiro_nome(supervisao) in supervisoes_da_praca
        },
        key=normalizar_texto
    )

opcoes_supervisao = ["Todas"] + supervisoes_disponiveis

with col_filtro_supervisao:
    supervisao_selecionada = st.selectbox("Supervisão", opcoes_supervisao)

with col_filtro_status:
    status_selecionado = st.selectbox("Status", ["Todos", "Realizadas", "Pendentes"])


df_filtrado = monitorias_google.copy()

if praca_selecionada != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Praça"] == praca_selecionada].copy()

if supervisao_selecionada != "Todas":
    df_filtrado = df_filtrado[
        df_filtrado["Supervisão"].astype(str).map(primeiro_nome)
        == primeiro_nome(supervisao_selecionada)
    ].copy()

if status_selecionado == "Realizadas":
    df_lista = df_filtrado[df_filtrado["Realizada"]].copy()
elif status_selecionado == "Pendentes":
    df_lista = df_filtrado[~df_filtrado["Realizada"]].copy()
else:
    df_lista = df_filtrado.copy()

# Status filtra as listas, mas não altera os indicadores e gráficos principais.
df_ativo = df_filtrado.copy()

filtros_ativos = []
if praca_selecionada != "Todas":
    filtros_ativos.append(f"<strong>Praça:</strong> {html.escape(praca_selecionada)}")
if supervisao_selecionada != "Todas":
    filtros_ativos.append(f"<strong>Supervisão:</strong> {html.escape(supervisao_selecionada)}")
if status_selecionado != "Todos":
    filtros_ativos.append(f"<strong>Status:</strong> {html.escape(status_selecionado)}")

if filtros_ativos:
    st.html('<div class="filter-summary">' + " &nbsp; • &nbsp; ".join(filtros_ativos) + '</div>')


st.html('<div id="indicadores"></div>')

# =========================================================
# INDICADORES
# =========================================================

total_colaboradores = len(df_ativo)
total_realizadas = int(df_ativo["Realizada"].sum())
total_pendentes = total_colaboradores - total_realizadas
percentual_concluido = (
    total_realizadas / total_colaboradores * 100
    if total_colaboradores else 0
)
notas_validas = df_ativo.loc[df_ativo["Média"].notna(), "Média"]
media_geral = notas_validas.mean() if not notas_validas.empty else None

col1, col2, col3, col4, col5 = st.columns(5)

metricas = [
    ("COLABORADORES", total_colaboradores, "no acompanhamento"),
    ("REALIZADAS", total_realizadas, "monitorias concluídas"),
    ("PENDENTES", total_pendentes, "monitorias a realizar"),
    ("CONCLUSÃO", f"{percentual_concluido:.1f}%", "do total"),
    ("MÉDIA", f"{media_geral:.1f}%" if media_geral is not None else "—", "notas registradas")
]

for coluna, (titulo, valor, subtitulo) in zip([col1, col2, col3, col4, col5], metricas):
    with coluna:
        st.html(
            f"""
            <div class="metric-card">
                <div class="metric-label">{titulo}</div>
                <div class="metric-value">{valor}</div>
                <div class="metric-foot">{subtitulo}</div>
            </div>
            """
        )


MESES = [
    "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
    "Jul", "Ago", "Set", "Out", "Nov", "Dez"
]


st.html('<div id="visao-geral"></div>')
st.html('<div id="evolucao"></div>')

# =========================================================
# GRÁFICOS PRINCIPAIS
# =========================================================

st.write("")
col_evolucao, col_status = st.columns([2.1, 1])

with col_evolucao:
    st.html(
        """
        <div class="panel-card">
            <div class="panel-card-title">Evolução das monitorias</div>
            <div class="panel-card-subtitle">Quantidade de monitorias realizadas por mês</div>
        </div>
        """
    )

    datas_validas = df_ativo.loc[df_ativo["Data Monitoria"].notna(), "Data Monitoria"]

    if not datas_validas.empty:
        primeiro_mes = datas_validas.min().to_period("M")
        ultimo_mes = max(datas_validas.max().to_period("M"), pd.Timestamp.now(tz="America/Sao_Paulo").tz_localize(None).to_period("M"))
        meses = pd.period_range(primeiro_mes, ultimo_mes, freq="M")
    else:
        meses = pd.period_range(pd.Timestamp.now(tz="America/Sao_Paulo").tz_localize(None).to_period("M"), pd.Timestamp.now(tz="America/Sao_Paulo").tz_localize(None).to_period("M"), freq="M")

    nomes_meses = []
    quantidades = []
    for periodo in meses:
        quantidade = df_ativo[
            (df_ativo["Data Monitoria"] >= periodo.start_time)
            & (df_ativo["Data Monitoria"] <= periodo.end_time)
        ].shape[0]
        nomes_meses.append(f"{MESES[periodo.month - 1]}/{str(periodo.year)[2:]}")
        quantidades.append(quantidade)

    fig_evolucao = go.Figure()
    fig_evolucao.add_trace(
        go.Scatter(
            x=nomes_meses,
            y=quantidades,
            mode="lines+markers",
            line=dict(color=PRIMARY, width=3),
            marker=dict(color=PRIMARY, size=7),
            hovertemplate="%{x}: %{y} monitorias<extra></extra>"
        )
    )
    fig_evolucao.update_layout(
        height=270,
        margin=dict(l=8, r=8, t=12, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=TEXT),
        xaxis=dict(showgrid=False, title=None),
        yaxis=dict(showgrid=True, gridcolor=BORDER, zeroline=False, title=None),
        showlegend=False
    )
    st.plotly_chart(fig_evolucao, use_container_width=True, config={"displayModeBar": False})

with col_status:
    st.html(
        """
        <div class="panel-card">
            <div class="panel-card-title">Status das monitorias</div>
            <div class="panel-card-subtitle">Distribuição do acompanhamento atual</div>
        </div>
        """
    )

    fig_status = go.Figure(
        go.Pie(
            values=[total_realizadas, total_pendentes],
            labels=["Realizadas", "Pendentes"],
            hole=.70,
            marker=dict(colors=[SUCCESS, WARNING]),
            textinfo="none",
            hovertemplate="%{label}: %{value}<extra></extra>"
        )
    )
    fig_status.update_layout(
        height=220,
        margin=dict(l=8, r=8, t=8, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        annotations=[dict(text=f"<b>{percentual_concluido:.0f}%</b><br><span style='font-size:10px'>concluído</span>", x=.5, y=.5, showarrow=False, font=dict(size=22, color=TEXT))]
    )
    st.plotly_chart(fig_status, use_container_width=True, config={"displayModeBar": False})

    st.html(
        f"""
        <div class="status-list">
            <div class="status-row"><span class="status-name">Realizadas</span><span class="status-number">{total_realizadas}</span></div>
            <div class="status-row"><span class="status-name">Pendentes</span><span class="status-number">{total_pendentes}</span></div>
        </div>
        """
    )


st.html('<div id="supervisores"></div>')

# =========================================================
# PRAÇAS E SUPERVISORES
# =========================================================

st.write("")
col_pracas, col_supervisores = st.columns(2)

with col_pracas:
    st.html(
        """
        <div class="panel-card">
            <div class="panel-card-title">Monitorias por praça</div>
            <div class="panel-card-subtitle">Volume de colaboradores no acompanhamento</div>
        </div>
        """
    )

    dados_pracas = (
        df_ativo.groupby("Praça", dropna=False)
        .size().reset_index(name="Quantidade")
    )
    dados_pracas["Praça"] = dados_pracas["Praça"].fillna("Sem praça")
    dados_pracas = dados_pracas.sort_values("Quantidade", ascending=True)

    fig_pracas = go.Figure(go.Bar(
        x=dados_pracas["Quantidade"],
        y=dados_pracas["Praça"],
        orientation="h",
        marker_color=PRIMARY,
        text=dados_pracas["Quantidade"],
        textposition="outside",
        hovertemplate="%{y}: %{x} colaboradores<extra></extra>"
    ))
    fig_pracas.update_layout(
        height=280,
        margin=dict(l=8, r=30, t=12, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=TEXT),
        xaxis=dict(showgrid=True, gridcolor=BORDER, zeroline=False, title=None),
        yaxis=dict(showgrid=False, title=None),
        showlegend=False
    )
    st.plotly_chart(fig_pracas, use_container_width=True, config={"displayModeBar": False})

with col_supervisores:
    st.html(
        """
        <div class="panel-card">
            <div class="panel-card-title">Monitorias por supervisão</div>
            <div class="panel-card-subtitle">Quantidade de colaboradores por equipe</div>
        </div>
        """
    )

    dados_supervisores = (
        df_ativo.assign(
            SupervisaoExibicao=df_ativo["Supervisão"].astype(str).map(
                lambda x: supervisao_canonica_por_primeiro_nome.get(primeiro_nome(x), x.strip().split()[0] if x.strip() else "")
            )
        )
        .groupby("SupervisaoExibicao", dropna=False)
        .size().reset_index(name="Quantidade")
        .sort_values("Quantidade", ascending=True)
    )

    fig_supervisores = go.Figure(go.Bar(
        x=dados_supervisores["Quantidade"],
        y=dados_supervisores["SupervisaoExibicao"],
        orientation="h",
        marker_color="#6680F2",
        text=dados_supervisores["Quantidade"],
        textposition="outside",
        hovertemplate="%{y}: %{x} colaboradores<extra></extra>"
    ))
    fig_supervisores.update_layout(
        height=280,
        margin=dict(l=8, r=30, t=12, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=TEXT),
        xaxis=dict(showgrid=True, gridcolor=BORDER, zeroline=False, title=None),
        yaxis=dict(showgrid=False, title=None),
        showlegend=False
    )
    st.plotly_chart(fig_supervisores, use_container_width=True, config={"displayModeBar": False})


st.html('<div id="pendencias"></div>')

# =========================================================
# PENDÊNCIAS E OUTRAS ETAPAS
# =========================================================

st.write("")
col_pendencias, col_etapas = st.columns([1.7, 1])

with col_pendencias:
    st.html(
        """
        <div class="panel-card">
            <div class="panel-card-title">Pendências</div>
            <div class="panel-card-subtitle">Colaboradores que ainda não possuem data de monitoria</div>
        </div>
        """
    )

    pendencias = df_lista[~df_lista["Realizada"]].copy()
    pendencias = pendencias.sort_values(["Supervisão", "Colaborador"], na_position="last")

    if pendencias.empty:
        st.html('<div class="panel-card"><div class="pending-meta">Nenhuma pendência nos filtros selecionados.</div></div>')
    else:
        with st.expander(f"Ver todas as {len(pendencias)} pendências", expanded=False):
            tabela_pendencias = pendencias[["Colaborador", "Função", "Supervisão", "Praça"]].copy()
            st.dataframe(tabela_pendencias, use_container_width=True, hide_index=True)

        pendencias_csv = pendencias[["Colaborador", "Função", "Supervisão", "Praça"]].copy()
        st.download_button(
            "Baixar pendências em CSV",
            data=pendencias_csv.to_csv(index=False).encode("utf-8-sig"),
            file_name="pendencias_monitorias.csv",
            mime="text/csv"
        )

with col_etapas:
    st.html('<div id="etapas"></div>')
    total_lado_a_lado = int(df_ativo["Data Lado a Lado"].notna().sum())
    total_offline = int(df_ativo["Data Monitoria Offline"].notna().sum())

    st.html(
        f"""
        <div class="panel-card">
            <div class="panel-card-title">Outras etapas</div>
            <div class="panel-card-subtitle">Acompanhamento complementar</div>
            <div class="status-list" style="margin-top:12px;">
                <div class="status-row"><span class="status-name">Lado a lado</span><span class="status-number">{total_lado_a_lado}</span></div>
                <div class="status-row"><span class="status-name">Monitoria offline</span><span class="status-number">{total_offline}</span></div>
            </div>
        </div>
        """
    )


# =========================================================
# DETALHE DA SUPERVISÃO
# =========================================================

if supervisao_selecionada != "Todas":
    st.write("")
    st.html(
        f"""
        <div class="panel-card">
            <div class="panel-card-title">Detalhamento • {html.escape(supervisao_selecionada)}</div>
            <div class="panel-card-subtitle">Colaboradores associados à supervisão selecionada</div>
        </div>
        """
    )

    df_detalhe = df_lista[["Colaborador", "Função", "Realizada", "Média"]].copy()
    df_detalhe["Status"] = df_detalhe["Realizada"].map({True: "Realizada", False: "Pendente"})
    df_detalhe["Média"] = df_detalhe["Média"].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "—")
    df_detalhe = df_detalhe[["Colaborador", "Função", "Status", "Média"]]
    st.dataframe(df_detalhe, use_container_width=True, hide_index=True)
