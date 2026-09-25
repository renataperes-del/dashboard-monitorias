import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import gspread
import html
import unicodedata
import hmac
import hashlib
import secrets
import smtplib
from email.message import EmailMessage

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
ABA_ACESSOS = "Acessos"
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


def gerar_hash_senha(senha, salt=None):

    if salt is None:
        salt = secrets.token_hex(16)

    hash_senha = hashlib.pbkdf2_hmac(
        "sha256",
        senha.encode("utf-8"),
        salt.encode("utf-8"),
        120000
    ).hex()

    return hash_senha, salt


def verificar_senha(senha, hash_senha, salt):

    hash_calculado, _ = gerar_hash_senha(senha, salt)

    return hmac.compare_digest(hash_calculado, str(hash_senha))


def carregar_acessos():

    gc = get_client()
    planilha = gc.open_by_key(SHEET_ID)
    aba_acessos = planilha.worksheet(ABA_ACESSOS)

    valores = aba_acessos.get_all_values()

    if not valores:
        return pd.DataFrame()

    cabecalhos = [str(x).strip() for x in valores[0]]

    for coluna in ["Senha Hash", "Salt"]:
        if coluna not in cabecalhos:
            cabecalhos.append(coluna)

    if cabecalhos != [str(x).strip() for x in valores[0]]:
        aba_acessos.update("A1", [cabecalhos])

    linhas = []

    for linha in valores[1:]:
        linha = list(linha)
        linha += [""] * (len(cabecalhos) - len(linha))
        linhas.append(linha[:len(cabecalhos)])

    if not linhas:
        return pd.DataFrame(columns=cabecalhos)

    df = pd.DataFrame(linhas, columns=cabecalhos)
    df["Usuário"] = df["Usuário"].astype(str).str.strip().str.casefold()

    return df


def registrar_acesso(usuario, perfil, nome):

    try:

        gc = get_client()
        planilha = gc.open_by_key(SHEET_ID)
        aba_log = planilha.worksheet(ABA_LOG)

        horario = datetime.now(
            ZoneInfo("America/Sao_Paulo")
        ).strftime("%d/%m/%Y %H:%M:%S")

        aba_log.append_row(
            [horario, usuario, perfil, nome],
            value_input_option="USER_ENTERED"
        )

    except Exception:
        pass


def salvar_nova_senha(usuario, senha):

    gc = get_client()
    planilha = gc.open_by_key(SHEET_ID)
    aba_acessos = planilha.worksheet(ABA_ACESSOS)

    valores = aba_acessos.get_all_values()

    if not valores:
        return False

    cabecalhos = valores[0]

    try:
        idx_usuario = cabecalhos.index("Usuário")
        idx_primeiro = cabecalhos.index("Primeiro acesso")
        idx_hash = cabecalhos.index("Senha Hash")
        idx_salt = cabecalhos.index("Salt")
    except ValueError:
        return False

    hash_senha, salt = gerar_hash_senha(senha)

    for numero_linha, linha in enumerate(valores[1:], start=2):

        usuario_planilha = (
            str(linha[idx_usuario]).strip().casefold()
            if len(linha) > idx_usuario
            else ""
        )

        if usuario_planilha == usuario:

            aba_acessos.update_cell(numero_linha, idx_hash + 1, hash_senha)
            aba_acessos.update_cell(numero_linha, idx_salt + 1, salt)
            aba_acessos.update_cell(numero_linha, idx_primeiro + 1, "Não")

            return True

    return False


def enviar_email_recuperacao_treinamento():

    smtp_host = st.secrets.get("smtp", {}).get("host", "smtp.office365.com")
    smtp_port = int(st.secrets.get("smtp", {}).get("port", 587))
    smtp_usuario = st.secrets.get("smtp", {}).get("usuario", "treinamento.comercial@nube.com.br")
    smtp_senha = st.secrets.get("smtp", {}).get("senha", "")
    email_destino = "treinamento.comercial@nube.com.br"

    if not smtp_senha:
        return False, "O envio de e-mail ainda não está configurado nos Secrets."

    mensagem = EmailMessage()
    mensagem["Subject"] = "Recuperação de acesso | Dashboard de Monitorias"
    mensagem["From"] = smtp_usuario
    mensagem["To"] = email_destino
    mensagem.set_content(
        "Olá!\n\n"
        "Foi solicitada a recuperação do acesso de Treinamento Comercial ao Dashboard de Monitorias.\n\n"
        f"Usuário: treinamento\nSenha de acesso: {senha_treinamento}\n\n"
        "Se você não solicitou esta recuperação, desconsidere este e-mail.\n"
    )

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as servidor:
            servidor.starttls()
            servidor.login(smtp_usuario, smtp_senha)
            servidor.send_message(mensagem)
        return True, None
    except Exception as erro:
        return False, str(erro)


def recuperar_senha(usuario):

    gc = get_client()
    planilha = gc.open_by_key(SHEET_ID)
    aba_acessos = planilha.worksheet(ABA_ACESSOS)

    valores = aba_acessos.get_all_values()

    if not valores:
        return False

    cabecalhos = valores[0]

    try:
        idx_usuario = cabecalhos.index("Usuário")
        idx_primeiro = cabecalhos.index("Primeiro acesso")
        idx_hash = cabecalhos.index("Senha Hash")
        idx_salt = cabecalhos.index("Salt")
    except ValueError:
        return False

    for numero_linha, linha in enumerate(valores[1:], start=2):

        usuario_planilha = (
            str(linha[idx_usuario]).strip().casefold()
            if len(linha) > idx_usuario
            else ""
        )

        if usuario_planilha == usuario:

            aba_acessos.update_cell(numero_linha, idx_hash + 1, "")
            aba_acessos.update_cell(numero_linha, idx_salt + 1, "")
            aba_acessos.update_cell(numero_linha, idx_primeiro + 1, "Sim")

            return True

    return False


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

try:
    df_acessos = carregar_acessos()
except Exception:
    st.error(
        "Não foi possível acessar a aba 'Acessos'. "
        "Verifique se as abas Acessos e Log_Acessos existem "
        "e se a conta de serviço está como Editor."
    )
    st.stop()

if "usuario_logado" not in st.session_state:
    st.session_state["usuario_logado"] = None
    st.session_state["perfil_acesso"] = None
    st.session_state["nome_acesso"] = None
    st.session_state["supervisao_acesso"] = None
    st.session_state["criando_senha"] = False
    st.session_state["recuperando_senha"] = False
    st.session_state["usuario_novo"] = None

if not st.session_state["usuario_logado"]:

    st.markdown(
        """
        <div style="text-align:center; margin:70px auto 22px;">
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

        if st.session_state["recuperando_senha"]:

            st.subheader("Recuperar senha")
            st.caption("Selecione seu nome para redefinir o acesso.")

            nomes_recuperacao = (
                df_acessos[["Usuário", "Nome"]]
                .dropna()
                .drop_duplicates()
            )

            nomes_recuperacao = nomes_recuperacao[
                nomes_recuperacao["Nome"].astype(str).str.strip() != ""
            ]

            opcoes_recuperacao = {
                str(row["Nome"]).strip(): str(row["Usuário"]).strip().casefold()
                for _, row in nomes_recuperacao.iterrows()
            }

            opcoes_recuperacao["Treinamento Comercial"] = "treinamento"

            nome_selecionado = st.selectbox(
                "Nome",
                ["Selecione seu nome"] + list(opcoes_recuperacao.keys())
            )

            if st.button("Recuperar acesso", use_container_width=True):

                if nome_selecionado == "Selecione seu nome":
                    st.warning("Selecione seu nome para continuar.")

                else:
                    usuario_recuperacao = opcoes_recuperacao[nome_selecionado]

                    if usuario_recuperacao == "treinamento":
                        sucesso, erro = enviar_email_recuperacao_treinamento()
                        if sucesso:
                            st.success(
                                "E-mail de recuperação enviado para treinamento.comercial@nube.com.br."
                            )
                        else:
                            st.error(f"Não foi possível enviar o e-mail de recuperação: {erro}")
                    elif recuperar_senha(usuario_recuperacao):
                        st.success(
                            "Acesso redefinido! Use sua senha provisória para entrar e crie uma nova senha."
                        )
                        st.session_state["recuperando_senha"] = False
                        st.rerun()
                    else:
                        st.error("Não foi possível redefinir o acesso.")

            st.info(
                "Para Treinamento Comercial, a recuperação será enviada por e-mail."
            )

            if st.button("Voltar para o login", use_container_width=True):
                st.session_state["recuperando_senha"] = False
                st.rerun()

        elif st.session_state["criando_senha"]:

            st.subheader("Crie sua senha")
            st.caption("Defina uma senha pessoal para os próximos acessos.")

            with st.form("form_nova_senha"):

                nova_senha = st.text_input("Nova senha", type="password")
                confirmar_senha = st.text_input("Confirmar nova senha", type="password")

                salvar_senha = st.form_submit_button(
                    "Salvar senha",
                    use_container_width=True
                )

            if salvar_senha:

                if len(nova_senha) < 8:
                    st.error("A senha deve ter pelo menos 8 caracteres.")

                elif nova_senha != confirmar_senha:
                    st.error("As senhas não coincidem.")

                elif salvar_nova_senha(
                    st.session_state["usuario_novo"],
                    nova_senha
                ):

                    st.session_state["criando_senha"] = False
                    st.success("Senha criada com sucesso! Faça seu login novamente.")
                    st.rerun()

                else:
                    st.error("Não foi possível salvar sua senha.")

            if st.button("Voltar para o login", use_container_width=True):
                st.session_state["criando_senha"] = False
                st.rerun()

        else:

            with st.form("form_login"):

                usuario_digitado = st.text_input("Usuário").strip().casefold()
                senha_digitada = st.text_input("Senha", type="password")

                entrar = st.form_submit_button(
                    "Entrar",
                    use_container_width=True
                )

            if entrar:

                registro = df_acessos[
                    df_acessos["Usuário"] == usuario_digitado
                ]

                perfil = None
                nome = None
                supervisao = None
                senha_valida = False
                precisa_criar_senha = False

                # Acesso exclusivo da área de Treinamento.
                # A senha fica no Streamlit Secrets e não depende da aba "Acessos".
                if usuario_digitado == "treinamento" and senha_treinamento:

                    perfil = "treinamento"
                    nome = "Treinamento Comercial"
                    senha_valida = hmac.compare_digest(
                        str(senha_digitada),
                        str(senha_treinamento)
                    )
                    precisa_criar_senha = False

                elif not registro.empty:

                    linha = registro.iloc[0]

                    perfil = str(linha.get("Perfil", "")).strip().casefold()
                    nome = str(linha.get("Nome", "")).strip()

                    hash_senha = str(linha.get("Senha Hash", "")).strip()
                    salt = str(linha.get("Salt", "")).strip()

                    primeiro_acesso = (
                        str(linha.get("Primeiro acesso", "")).strip().casefold()
                        == "sim"
                    )

                    if hash_senha and salt:

                        senha_valida = verificar_senha(
                            senha_digitada,
                            hash_senha,
                            salt
                        )

                    else:

                        senha_provisoria = (
                            senhas_supervisores.get(usuario_digitado)
                            if perfil == "supervisor"
                            else senhas_gerentes.get(usuario_digitado)
                        )

                        senha_valida = (
                            senha_provisoria is not None
                            and hmac.compare_digest(
                                str(senha_digitada),
                                str(senha_provisoria)
                            )
                        )

                    precisa_criar_senha = primeiro_acesso or not hash_senha

                if senha_valida and perfil in {"supervisor", "gerente", "treinamento"}:

                    if precisa_criar_senha:

                        st.session_state["usuario_novo"] = usuario_digitado
                        st.session_state["criando_senha"] = True
                        st.rerun()

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

            if st.button("Esqueci minha senha", use_container_width=True):
                st.session_state["recuperando_senha"] = True
                st.rerun()

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