"""
=====================================================================
 ALPHA TÊXTIL — Gerenciador Profissional de Precificação e Gestão
 Aplicativo único (Streamlit) para precificação de produtos na Shopee.

 Como executar:
   pip install streamlit pandas plotly
   streamlit run app.py

 Acesso padrão (pode ser alterado depois do primeiro login):
   e-mail  : admin@alphatextil.com.br
   senha   : alpha2026

 Observação sobre as taxas da Shopee:
 Os valores padrão de comissão/taxa fixa usados neste app refletem a
 estrutura escalonada por faixa de preço vigente desde 01/03/2026.
 Como a Shopee pode alterar esses valores a qualquer momento, TODOS
 os percentuais e taxas ficam editáveis na aba "Configurações" —
 confirme sempre os valores atuais no Seller Centre.
=====================================================================
"""

import io
import os
import json
import hashlib
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# =====================================================================
# CONFIGURAÇÃO GERAL DA PÁGINA
# =====================================================================
st.set_page_config(
    page_title="Alpha Têxtil | Gestão Shopee",
    page_icon="🧵",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_DIR, "alpha_textil.db")

APP_NOME = "Alpha Têxtil"
DEFAULT_ADMIN_NOME = "Administrador"
DEFAULT_ADMIN_EMAIL = "admin@alphatextil.com.br"
DEFAULT_ADMIN_SENHA = "alpha2026"

CATEGORIAS_PADRAO = [
    "Tecidos", "Cama, Mesa e Banho", "Vestuário", "Aviamentos",
    "Artesanato", "Moda Praia", "Acessórios", "Outros",
]

# Faixas de comissão/taxa fixa Shopee (referência 2026 — editável na aba Configurações)
FEE_TIERS_PADRAO = [
    {"min": 0.00,   "max": 7.99,      "comissao_pct": 20.0, "taxa_fixa": 50.0, "taxa_fixa_pct": True},
    {"min": 8.00,   "max": 79.99,     "comissao_pct": 20.0, "taxa_fixa": 4.00, "taxa_fixa_pct": False},
    {"min": 80.00,  "max": 99.99,     "comissao_pct": 14.0, "taxa_fixa": 16.00, "taxa_fixa_pct": False},
    {"min": 100.00, "max": 199.99,    "comissao_pct": 14.0, "taxa_fixa": 20.00, "taxa_fixa_pct": False},
    {"min": 200.00, "max": 999999.99, "comissao_pct": 14.0, "taxa_fixa": 26.00, "taxa_fixa_pct": False},
]

CONFIG_PADRAO = {
    "fee_tiers": FEE_TIERS_PADRAO,
    "imposto_pct": 6.0,
    "outras_taxas_pct": 0.0,
    "margem_padrao_pct": 30.0,
    "cpf_taxa_extra": 3.0,
}


# =====================================================================
# IDENTIDADE VISUAL — CSS (fundo claro, preto absoluto, degradê laranja)
# =====================================================================
def aplicar_estilo():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700;800&family=Inter:wght@400;500;600&display=swap');

        :root {
            --at-bg: #F3F3F1;
            --at-surface: #FFFFFF;
            --at-black: #121212;
            --at-gray: #63635E;
            --at-border: #E4E3DF;
            --at-orange-1: #FF6A00;
            --at-orange-2: #FFB020;
            --at-gradient: linear-gradient(135deg, var(--at-orange-1) 0%, var(--at-orange-2) 100%);
            --at-success: #1E8E5A;
            --at-danger: #D8402F;
        }

        html, body, [class*="css"], .stMarkdown, p, span, label, div {
            font-family: 'Inter', -apple-system, sans-serif;
        }
        h1, h2, h3, h4, h5, .at-heading {
            font-family: 'Poppins', sans-serif !important;
            color: var(--at-black) !important;
            font-weight: 700 !important;
        }

        [data-testid="stAppViewContainer"] { background: var(--at-bg); }
        [data-testid="stHeader"] { background: rgba(0,0,0,0); }
        .block-container { padding-top: 2rem; }

        /* ---------- Sidebar ---------- */
        [data-testid="stSidebar"] {
            background: #101010;
            border-right: 3px solid #FF6A00;
        }
        [data-testid="stSidebar"] * { color: #F2F2EF !important; }
        [data-testid="stSidebar"] hr { border-color: #2A2A2A; }

        .at-logo {
            font-family: 'Poppins', sans-serif;
            font-weight: 800;
            font-size: 1.55rem;
            line-height: 1.1;
            background: var(--at-gradient);
            -webkit-background-clip: text;
            background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0px;
        }
        .at-logo-sub {
            color: #9C9C97 !important;
            font-size: 0.72rem;
            letter-spacing: 1.5px;
            margin-top: -2px;
        }
        .at-chip {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 20px;
            background: rgba(255,106,0,0.15);
            color: #FFB020 !important;
            font-size: 0.72rem;
            font-weight: 600;
            border: 1px solid rgba(255,106,0,0.4);
        }

        /* ---------- Botões ---------- */
        .stButton > button, .stFormSubmitButton > button, .stDownloadButton > button {
            background: var(--at-gradient);
            color: #fff !important;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            padding: 0.55rem 1.1rem;
            box-shadow: 0 4px 14px rgba(255,106,0,0.25);
            transition: transform 0.12s ease, box-shadow 0.12s ease;
        }
        .stButton > button:hover, .stFormSubmitButton > button:hover, .stDownloadButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 18px rgba(255,106,0,0.38);
            color: #fff !important;
        }
        button[kind="secondary"] {
            background: #fff !important;
            color: var(--at-black) !important;
            border: 1.5px solid var(--at-border) !important;
            box-shadow: none !important;
        }

        /* ---------- Abas ---------- */
        button[data-baseweb="tab"] {
            font-family: 'Poppins', sans-serif;
            font-weight: 600;
            color: var(--at-gray);
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            color: var(--at-black) !important;
            border-bottom: 3px solid var(--at-orange-1);
        }
        [data-baseweb="tab-highlight"] { background-color: var(--at-orange-1) !important; }

        /* ---------- Métricas / cards ---------- */
        [data-testid="stMetric"] {
            background: var(--at-surface);
            border: 1px solid var(--at-border);
            border-left: 4px solid var(--at-orange-1);
            border-radius: 10px;
            padding: 0.9rem 1.1rem;
        }
        [data-testid="stMetricLabel"] { color: var(--at-gray) !important; }
        [data-testid="stMetricValue"] { color: var(--at-black) !important; font-family: 'Poppins', sans-serif; }

        /* ---------- Cartão de resultado da precificação ---------- */
        .at-price-card {
            background: #121212;
            border-radius: 16px;
            padding: 1.6rem 1.8rem;
            color: #fff;
        }
        .at-price-label { color: #B8B8B2; font-size: 0.85rem; letter-spacing: 0.5px; }
        .at-price-value {
            font-family: 'Poppins', sans-serif;
            font-weight: 800;
            font-size: 2.6rem;
            background: var(--at-gradient);
            -webkit-background-clip: text;
            background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        /* ---------- Login ---------- */
        .login-card {
            background: var(--at-surface);
            border: 1px solid var(--at-border);
            border-radius: 18px;
            padding: 2.2rem 2.1rem 1.4rem 2.1rem;
            box-shadow: 0 24px 60px rgba(0,0,0,0.07);
            margin-top: 1.2rem;
        }
        .login-title {
            font-family: 'Poppins', sans-serif;
            font-weight: 800;
            font-size: 2rem;
            background: var(--at-gradient);
            -webkit-background-clip: text;
            background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 0px;
        }
        .login-sub {
            text-align: center;
            color: var(--at-gray);
            font-size: 0.92rem;
            margin-top: 0px;
            margin-bottom: 1.3rem;
        }

        /* ---------- Divisores e textos auxiliares ---------- */
        hr { border-color: var(--at-border); }
        .at-note {
            background: #FFF6EC;
            border: 1px solid #FFDBA8;
            border-radius: 10px;
            padding: 0.8rem 1rem;
            color: #7A4A00;
            font-size: 0.88rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# =====================================================================
# BANCO DE DADOS (SQLite)
# =====================================================================
@st.cache_resource
def get_conn():
    import sqlite3
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha_salt TEXT NOT NULL,
            senha_hash TEXT NOT NULL,
            criado_em TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT NOT NULL UNIQUE,
            nome TEXT NOT NULL,
            categoria TEXT,
            custo_unitario REAL NOT NULL DEFAULT 0,
            peso_kg REAL,
            comprimento_cm REAL,
            largura_cm REAL,
            altura_cm REAL,
            fornecedor TEXT,
            estoque INTEGER DEFAULT 0,
            ativo INTEGER DEFAULT 1,
            criado_por TEXT,
            criado_em TEXT,
            atualizado_em TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS historico_precos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER,
            produto_nome TEXT,
            produto_sku TEXT,
            custo_produto REAL,
            custo_embalagem REAL,
            custo_frete REAL,
            tipo_vendedor TEXT,
            faixa_comissao_pct REAL,
            faixa_taxa_fixa REAL,
            imposto_pct REAL,
            outras_taxas_pct REAL,
            margem_desejada_pct REAL,
            preco_sugerido REAL,
            preco_minimo REAL,
            lucro_liquido REAL,
            margem_real_pct REAL,
            calculado_por TEXT,
            calculado_em TEXT,
            FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE SET NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS configuracoes (
            chave TEXT PRIMARY KEY,
            valor TEXT
        )
    """)
    conn.commit()
    _criar_admin_padrao(conn)
    _garantir_configuracoes_padrao(conn)


def _criar_admin_padrao(conn):
    cur = conn.cursor()
    cur.execute("SELECT id FROM usuarios WHERE email = ?", (DEFAULT_ADMIN_EMAIL,))
    if cur.fetchone() is None:
        salt, h = gerar_hash_senha(DEFAULT_ADMIN_SENHA)
        cur.execute(
            "INSERT INTO usuarios (nome, email, senha_salt, senha_hash, criado_em) VALUES (?, ?, ?, ?, ?)",
            (DEFAULT_ADMIN_NOME, DEFAULT_ADMIN_EMAIL, salt, h, datetime.now().isoformat()),
        )
        conn.commit()


def _garantir_configuracoes_padrao(conn):
    for chave, valor in CONFIG_PADRAO.items():
        if get_config(chave) is None:
            set_config(chave, valor)


def get_config(chave, padrao=None):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT valor FROM configuracoes WHERE chave = ?", (chave,))
    row = cur.fetchone()
    if row is None:
        return padrao
    try:
        return json.loads(row[0])
    except (TypeError, json.JSONDecodeError):
        return row[0]


def set_config(chave, valor):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO configuracoes (chave, valor) VALUES (?, ?) "
        "ON CONFLICT(chave) DO UPDATE SET valor = excluded.valor",
        (chave, json.dumps(valor)),
    )
    conn.commit()


# =====================================================================
# AUTENTICAÇÃO
# =====================================================================
def gerar_hash_senha(senha: str, salt: bytes = None):
    if salt is None:
        salt = os.urandom(16)
    hash_bytes = hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), salt, 100_000)
    return salt.hex(), hash_bytes.hex()


def verificar_senha(senha: str, salt_hex: str, hash_hex: str) -> bool:
    salt = bytes.fromhex(salt_hex)
    _, novo_hash = gerar_hash_senha(senha, salt)
    return novo_hash == hash_hex


def autenticar(email: str, senha: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, nome, email, senha_salt, senha_hash FROM usuarios WHERE email = ?", (email,))
    row = cur.fetchone()
    if row is None:
        return None
    uid, nome, email_db, salt, h = row
    if verificar_senha(senha, salt, h):
        return {"id": uid, "nome": nome, "email": email_db}
    return None


def cadastrar_usuario(nome: str, email: str, senha: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM usuarios WHERE email = ?", (email,))
    if cur.fetchone() is not None:
        return False, "Já existe uma conta cadastrada com este e-mail."
    salt, h = gerar_hash_senha(senha)
    cur.execute(
        "INSERT INTO usuarios (nome, email, senha_salt, senha_hash, criado_em) VALUES (?, ?, ?, ?, ?)",
        (nome, email, salt, h, datetime.now().isoformat()),
    )
    conn.commit()
    return True, "Conta criada com sucesso."


def listar_usuarios():
    conn = get_conn()
    return pd.read_sql_query("SELECT id, nome, email, criado_em FROM usuarios ORDER BY criado_em", conn)


def excluir_usuario(user_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM usuarios WHERE id = ?", (user_id,))
    conn.commit()


# =====================================================================
# FORMATAÇÃO (padrão brasileiro)
# =====================================================================
def formatar_moeda(valor):
    if valor is None:
        return "—"
    texto = f"{valor:,.2f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def formatar_pct(valor, casas=1):
    if valor is None:
        return "—"
    return f"{valor:.{casas}f}%".replace(".", ",")


def formatar_data(iso_str):
    try:
        return datetime.fromisoformat(iso_str).strftime("%d/%m/%Y %H:%M")
    except (ValueError, TypeError):
        return iso_str or "—"


# =====================================================================
# LÓGICA DE PRECIFICAÇÃO (Shopee)
# =====================================================================
def calcular_precificacao(custo_produto, custo_embalagem, custo_frete, cpf,
                           imposto_pct, outras_taxas_pct, margem_pct,
                           tiers, cpf_taxa_extra):
    """Resolve o preço de venda que satisfaz a faixa de comissão/taxa fixa
    correspondente, considerando todos os custos percentuais e fixos."""
    fixos_base = custo_produto + custo_embalagem + custo_frete + (cpf_taxa_extra if cpf else 0.0)
    tiers_ordenados = sorted(tiers, key=lambda t: t["min"])

    candidato_fallback = None
    for tier in tiers_ordenados:
        comissao_pct = tier["comissao_pct"]
        if tier.get("taxa_fixa_pct"):
            pct_extra = tier["taxa_fixa"]
            fixos_tier = fixos_base
        else:
            pct_extra = 0.0
            fixos_tier = fixos_base + tier["taxa_fixa"]

        pct_total = (comissao_pct + margem_pct + imposto_pct + outras_taxas_pct + pct_extra) / 100.0
        denom = 1.0 - pct_total
        if denom <= 0:
            continue
        preco = fixos_tier / denom
        candidato_fallback = candidato_fallback or {"preco": preco, "tier": tier, "aproximado": True}
        if tier["min"] <= preco <= tier["max"]:
            return {"preco": preco, "tier": tier, "aproximado": False}

    if candidato_fallback is not None:
        return candidato_fallback
    return {"preco": None, "tier": tiers_ordenados[-1], "aproximado": True}


def detalhar_precificacao(preco, tier, custo_produto, custo_embalagem, custo_frete,
                           cpf, cpf_taxa_extra, imposto_pct, outras_taxas_pct):
    comissao_valor = preco * tier["comissao_pct"] / 100.0
    if tier.get("taxa_fixa_pct"):
        taxa_fixa_valor = preco * tier["taxa_fixa"] / 100.0
    else:
        taxa_fixa_valor = tier["taxa_fixa"]
    imposto_valor = preco * imposto_pct / 100.0
    outras_valor = preco * outras_taxas_pct / 100.0
    cpf_valor = cpf_taxa_extra if cpf else 0.0

    custos_totais = (custo_produto + custo_embalagem + custo_frete + cpf_valor
                      + comissao_valor + taxa_fixa_valor + imposto_valor + outras_valor)
    lucro_liquido = preco - custos_totais
    margem_real_pct = (lucro_liquido / preco * 100.0) if preco else 0.0

    return {
        "comissao_valor": comissao_valor,
        "taxa_fixa_valor": taxa_fixa_valor,
        "imposto_valor": imposto_valor,
        "outras_valor": outras_valor,
        "cpf_valor": cpf_valor,
        "lucro_liquido": lucro_liquido,
        "margem_real_pct": margem_real_pct,
    }


# =====================================================================
# CRUD — PRODUTOS
# =====================================================================
def listar_produtos(somente_ativos=False):
    conn = get_conn()
    query = "SELECT * FROM produtos"
    if somente_ativos:
        query += " WHERE ativo = 1"
    query += " ORDER BY nome"
    return pd.read_sql_query(query, conn)


def obter_produto(produto_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
    row = cur.fetchone()
    if row is None:
        return None
    cols = [d[0] for d in cur.description]
    return dict(zip(cols, row))


def salvar_produto(dados, produto_id=None, usuario_nome=""):
    conn = get_conn()
    cur = conn.cursor()
    agora = datetime.now().isoformat()
    cur.execute("SELECT id FROM produtos WHERE sku = ? AND id IS NOT ?", (dados["sku"], produto_id or -1))
    if cur.fetchone() is not None:
        return False, "Já existe um produto com este SKU."

    if produto_id is None:
        cur.execute("""
            INSERT INTO produtos (sku, nome, categoria, custo_unitario, peso_kg,
                comprimento_cm, largura_cm, altura_cm, fornecedor, estoque, ativo,
                criado_por, criado_em, atualizado_em)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?)
        """, (dados["sku"], dados["nome"], dados["categoria"], dados["custo_unitario"],
              dados["peso_kg"], dados["comprimento_cm"], dados["largura_cm"], dados["altura_cm"],
              dados["fornecedor"], dados["estoque"], usuario_nome, agora, agora))
    else:
        cur.execute("""
            UPDATE produtos SET sku=?, nome=?, categoria=?, custo_unitario=?, peso_kg=?,
                comprimento_cm=?, largura_cm=?, altura_cm=?, fornecedor=?, estoque=?, atualizado_em=?
            WHERE id = ?
        """, (dados["sku"], dados["nome"], dados["categoria"], dados["custo_unitario"],
              dados["peso_kg"], dados["comprimento_cm"], dados["largura_cm"], dados["altura_cm"],
              dados["fornecedor"], dados["estoque"], agora, produto_id))
    conn.commit()
    return True, "Produto salvo com sucesso."


def excluir_produto(produto_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
    conn.commit()


# =====================================================================
# HISTÓRICO DE PRECIFICAÇÃO
# =====================================================================
def salvar_historico(registro):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO historico_precos (
            produto_id, produto_nome, produto_sku, custo_produto, custo_embalagem,
            custo_frete, tipo_vendedor, faixa_comissao_pct, faixa_taxa_fixa,
            imposto_pct, outras_taxas_pct, margem_desejada_pct, preco_sugerido,
            preco_minimo, lucro_liquido, margem_real_pct, calculado_por, calculado_em
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        registro.get("produto_id"), registro["produto_nome"], registro.get("produto_sku"),
        registro["custo_produto"], registro["custo_embalagem"], registro["custo_frete"],
        registro["tipo_vendedor"], registro["faixa_comissao_pct"], registro["faixa_taxa_fixa"],
        registro["imposto_pct"], registro["outras_taxas_pct"], registro["margem_desejada_pct"],
        registro["preco_sugerido"], registro["preco_minimo"], registro["lucro_liquido"],
        registro["margem_real_pct"], registro["calculado_por"], datetime.now().isoformat(),
    ))
    conn.commit()


def listar_historico():
    conn = get_conn()
    return pd.read_sql_query("SELECT * FROM historico_precos ORDER BY calculado_em DESC", conn)


def excluir_historico(hist_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM historico_precos WHERE id = ?", (hist_id,))
    conn.commit()


# =====================================================================
# TELA DE LOGIN / CADASTRO
# =====================================================================
def tela_login():
    aplicar_estilo()
    _, col_meio, _ = st.columns([1, 1.25, 1])
    with col_meio:
        st.markdown("<div class='login-card'>", unsafe_allow_html=True)
        st.markdown("<div class='login-title'>🧵 ALPHA TÊXTIL</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='login-sub'>Gerenciador de Precificação e Gestão · Shopee</div>",
            unsafe_allow_html=True,
        )

        aba_login, aba_cadastro = st.tabs(["Entrar", "Criar conta"])

        with aba_login:
            with st.form("form_login", clear_on_submit=False):
                email = st.text_input("E-mail", placeholder="voce@alphatextil.com.br")
                senha = st.text_input("Senha", type="password", placeholder="••••••••")
                entrar = st.form_submit_button("Entrar", use_container_width=True)
            if entrar:
                if not email or not senha:
                    st.error("Preencha e-mail e senha.")
                else:
                    usuario = autenticar(email.strip().lower(), senha)
                    if usuario:
                        st.session_state.usuario = usuario
                        st.rerun()
                    else:
                        st.error("E-mail ou senha inválidos.")
            st.caption("Acesso padrão: **admin@alphatextil.com.br** · senha **alpha2026**")

        with aba_cadastro:
            with st.form("form_cadastro", clear_on_submit=True):
                nome_novo = st.text_input("Nome completo")
                email_novo = st.text_input("E-mail corporativo")
                senha_novo = st.text_input("Senha", type="password")
                senha_confirma = st.text_input("Confirmar senha", type="password")
                criar = st.form_submit_button("Criar conta", use_container_width=True)
            if criar:
                if not nome_novo or not email_novo or not senha_novo:
                    st.error("Preencha todos os campos.")
                elif "@" not in email_novo or "." not in email_novo:
                    st.error("Informe um e-mail válido.")
                elif len(senha_novo) < 6:
                    st.error("A senha deve ter pelo menos 6 caracteres.")
                elif senha_novo != senha_confirma:
                    st.error("As senhas não coincidem.")
                else:
                    ok, msg = cadastrar_usuario(nome_novo.strip(), email_novo.strip().lower(), senha_novo)
                    if ok:
                        st.success(f"{msg} Vá para a aba **Entrar** para acessar o sistema.")
                    else:
                        st.error(msg)

        st.markdown("</div>", unsafe_allow_html=True)


# =====================================================================
# ABA: DASHBOARD
# =====================================================================
def dashboard_tab():
    st.subheader("Visão geral da operação")

    produtos = listar_produtos()
    historico = listar_historico()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Produtos cadastrados", len(produtos))
    col2.metric("Cálculos de preço realizados", len(historico))

    if not historico.empty:
        margem_media = historico["margem_real_pct"].mean()
        preco_medio = historico["preco_sugerido"].mean()
        col3.metric("Margem real média", formatar_pct(margem_media))
        col4.metric("Preço médio sugerido", formatar_moeda(preco_medio))
    else:
        col3.metric("Margem real média", "—")
        col4.metric("Preço médio sugerido", "—")

    st.markdown("")

    if historico.empty and produtos.empty:
        st.info(
            "Ainda não há produtos ou cálculos registrados. Cadastre um produto na aba "
            "**Produtos** e faça sua primeira precificação na aba **Precificação**."
        )
        return

    col_graf1, col_graf2 = st.columns(2)

    with col_graf1:
        if not produtos.empty:
            contagem_cat = produtos["categoria"].fillna("Sem categoria").value_counts().reset_index()
            contagem_cat.columns = ["Categoria", "Quantidade"]
            fig = px.bar(
                contagem_cat, x="Categoria", y="Quantidade",
                title="Produtos por categoria",
                color_discrete_sequence=["#FF6A00"],
            )
            fig.update_layout(
                paper_bgcolor="#F3F3F1", plot_bgcolor="#FFFFFF",
                font_color="#121212", title_font_family="Poppins",
                margin=dict(t=50, l=10, r=10, b=10),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Cadastre produtos para ver a distribuição por categoria.")

    with col_graf2:
        if not historico.empty:
            hist_ordenado = historico.sort_values("calculado_em")
            hist_ordenado["calculado_em_fmt"] = pd.to_datetime(hist_ordenado["calculado_em"])
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=hist_ordenado["calculado_em_fmt"], y=hist_ordenado["margem_real_pct"],
                mode="lines+markers", name="Margem real (%)",
                line=dict(color="#FF6A00", width=3),
                marker=dict(color="#FFB020"),
            ))
            fig2.update_layout(
                title="Evolução da margem real por cálculo",
                paper_bgcolor="#F3F3F1", plot_bgcolor="#FFFFFF",
                font_color="#121212", title_font_family="Poppins",
                margin=dict(t=50, l=10, r=10, b=10),
                yaxis_title="Margem (%)", xaxis_title="",
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Faça cálculos de precificação para ver a evolução de margem.")

    if not historico.empty:
        st.markdown("##### Últimos cálculos")
        tabela = historico.head(8)[[
            "produto_nome", "preco_sugerido", "margem_real_pct", "lucro_liquido", "calculado_por", "calculado_em"
        ]].copy()
        tabela["preco_sugerido"] = tabela["preco_sugerido"].apply(formatar_moeda)
        tabela["margem_real_pct"] = tabela["margem_real_pct"].apply(formatar_pct)
        tabela["lucro_liquido"] = tabela["lucro_liquido"].apply(formatar_moeda)
        tabela["calculado_em"] = tabela["calculado_em"].apply(formatar_data)
        tabela.columns = ["Produto", "Preço sugerido", "Margem real", "Lucro líquido", "Calculado por", "Quando"]
        st.dataframe(tabela, use_container_width=True, hide_index=True)


# =====================================================================
# ABA: PRODUTOS
# =====================================================================
def produtos_tab(usuario):
    st.subheader("Cadastro de produtos")

    sub_novo, sub_lista = st.tabs(["➕ Novo produto", "📋 Produtos cadastrados"])

    with sub_novo:
        with st.form("form_novo_produto", clear_on_submit=True):
            c1, c2 = st.columns(2)
            sku = c1.text_input("SKU *", placeholder="Ex: TEC-001")
            nome = c2.text_input("Nome do produto *", placeholder="Ex: Tecido Oxford Azul 1m")
            categoria = c1.selectbox("Categoria", CATEGORIAS_PADRAO)
            fornecedor = c2.text_input("Fornecedor", placeholder="Opcional")

            c3, c4, c5 = st.columns(3)
            custo = c3.number_input("Custo unitário (R$) *", min_value=0.0, step=0.5, format="%.2f")
            estoque = c4.number_input("Estoque (un.)", min_value=0, step=1)
            peso = c5.number_input("Peso (kg)", min_value=0.0, step=0.05, format="%.3f")

            c6, c7 = st.columns(2)
            with c6:
                cc1, cc2 = st.columns(2)
                comprimento = cc1.number_input("Comprimento (cm)", min_value=0.0, step=1.0)
                largura = cc2.number_input("Largura (cm)", min_value=0.0, step=1.0)
            with c7:
                altura = st.number_input("Altura (cm)", min_value=0.0, step=1.0)

            enviar = st.form_submit_button("Salvar produto", use_container_width=True)

        if enviar:
            if not sku or not nome or custo <= 0:
                st.error("Preencha SKU, nome e um custo unitário maior que zero.")
            else:
                dados = {
                    "sku": sku.strip(), "nome": nome.strip(), "categoria": categoria,
                    "custo_unitario": custo, "peso_kg": peso or None,
                    "comprimento_cm": comprimento or None, "largura_cm": largura or None,
                    "altura_cm": altura or None, "fornecedor": fornecedor.strip() or None,
                    "estoque": int(estoque),
                }
                ok, msg = salvar_produto(dados, usuario_nome=usuario["nome"])
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    with sub_lista:
        produtos = listar_produtos()
        if produtos.empty:
            st.info("Nenhum produto cadastrado ainda.")
        else:
            busca = st.text_input("🔎 Buscar por SKU ou nome", "")
            filtrado = produtos
            if busca:
                mask = (
                    produtos["sku"].str.contains(busca, case=False, na=False)
                    | produtos["nome"].str.contains(busca, case=False, na=False)
                )
                filtrado = produtos[mask]

            tabela = filtrado[["sku", "nome", "categoria", "custo_unitario", "estoque", "fornecedor"]].copy()
            tabela["custo_unitario"] = tabela["custo_unitario"].apply(formatar_moeda)
            tabela.columns = ["SKU", "Nome", "Categoria", "Custo unitário", "Estoque", "Fornecedor"]
            st.dataframe(tabela, use_container_width=True, hide_index=True)

            csv_buffer = io.StringIO()
            filtrado.to_csv(csv_buffer, index=False)
            st.download_button(
                "⬇️ Exportar produtos (CSV)", csv_buffer.getvalue(),
                file_name="produtos_alpha_textil.csv", mime="text/csv",
            )

            st.markdown("---")
            st.markdown("##### Editar ou excluir produto")
            opcoes = {f"{row.sku} — {row.nome}": row.id for row in filtrado.itertuples()}
            if opcoes:
                escolha = st.selectbox("Selecione um produto", list(opcoes.keys()))
                produto_id = opcoes[escolha]
                produto = obter_produto(produto_id)

                with st.form(f"form_editar_{produto_id}"):
                    c1, c2 = st.columns(2)
                    sku_e = c1.text_input("SKU *", value=produto["sku"])
                    nome_e = c2.text_input("Nome do produto *", value=produto["nome"])
                    idx_cat = CATEGORIAS_PADRAO.index(produto["categoria"]) if produto["categoria"] in CATEGORIAS_PADRAO else 0
                    categoria_e = c1.selectbox("Categoria", CATEGORIAS_PADRAO, index=idx_cat)
                    fornecedor_e = c2.text_input("Fornecedor", value=produto["fornecedor"] or "")

                    c3, c4, c5 = st.columns(3)
                    custo_e = c3.number_input("Custo unitário (R$) *", min_value=0.0,
                                               value=float(produto["custo_unitario"] or 0), step=0.5, format="%.2f")
                    estoque_e = c4.number_input("Estoque (un.)", min_value=0,
                                                 value=int(produto["estoque"] or 0), step=1)
                    peso_e = c5.number_input("Peso (kg)", min_value=0.0,
                                              value=float(produto["peso_kg"] or 0), step=0.05, format="%.3f")

                    c6, c7, c8 = st.columns(3)
                    comprimento_e = c6.number_input("Comprimento (cm)", min_value=0.0,
                                                      value=float(produto["comprimento_cm"] or 0), step=1.0)
                    largura_e = c7.number_input("Largura (cm)", min_value=0.0,
                                                  value=float(produto["largura_cm"] or 0), step=1.0)
                    altura_e = c8.number_input("Altura (cm)", min_value=0.0,
                                                 value=float(produto["altura_cm"] or 0), step=1.0)

                    col_a, col_b = st.columns(2)
                    salvar_edicao = col_a.form_submit_button("💾 Salvar alterações", use_container_width=True)
                    confirmar_exclusao = col_b.checkbox("Confirmo a exclusão deste produto")

                if salvar_edicao:
                    if not sku_e or not nome_e or custo_e <= 0:
                        st.error("Preencha SKU, nome e um custo unitário maior que zero.")
                    else:
                        dados_e = {
                            "sku": sku_e.strip(), "nome": nome_e.strip(), "categoria": categoria_e,
                            "custo_unitario": custo_e, "peso_kg": peso_e or None,
                            "comprimento_cm": comprimento_e or None, "largura_cm": largura_e or None,
                            "altura_cm": altura_e or None, "fornecedor": fornecedor_e.strip() or None,
                            "estoque": int(estoque_e),
                        }
                        ok, msg = salvar_produto(dados_e, produto_id=produto_id, usuario_nome=usuario["nome"])
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

                if confirmar_exclusao:
                    if st.button("🗑️ Excluir produto definitivamente", type="secondary"):
                        excluir_produto(produto_id)
                        st.success("Produto excluído.")
                        st.rerun()


# =====================================================================
# ABA: CALCULADORA DE PRECIFICAÇÃO
# =====================================================================
def precificacao_tab(usuario):
    st.subheader("Calculadora de precificação — Shopee")

    tiers = get_config("fee_tiers", FEE_TIERS_PADRAO)
    imposto_padrao = get_config("imposto_pct", 6.0)
    outras_padrao = get_config("outras_taxas_pct", 0.0)
    margem_padrao = get_config("margem_padrao_pct", 30.0)
    cpf_taxa_extra = get_config("cpf_taxa_extra", 3.0)

    produtos = listar_produtos(somente_ativos=True)
    opcoes_produto = ["— Preenchimento manual —"] + [
        f"{row.sku} — {row.nome}" for row in produtos.itertuples()
    ]
    escolha_produto = st.selectbox("Carregar dados de um produto cadastrado (opcional)", opcoes_produto)

    produto_selecionado = None
    if escolha_produto != "— Preenchimento manual —":
        sku_escolhido = escolha_produto.split(" — ")[0]
        produto_selecionado = produtos[produtos["sku"] == sku_escolhido].iloc[0]

    with st.form("form_precificacao"):
        c1, c2, c3 = st.columns(3)
        custo_produto = c1.number_input(
            "Custo do produto (R$) *", min_value=0.0, step=0.5, format="%.2f",
            value=float(produto_selecionado["custo_unitario"]) if produto_selecionado is not None else 0.0,
        )
        custo_embalagem = c2.number_input("Custo de embalagem (R$)", min_value=0.0, step=0.5, format="%.2f", value=0.0)
        custo_frete = c3.number_input("Frete adicional pago pelo vendedor (R$)", min_value=0.0, step=0.5, format="%.2f", value=0.0)

        c4, c5, c6 = st.columns(3)
        tipo_vendedor = c4.radio("Tipo de vendedor", ["CNPJ", "CPF"], horizontal=True)
        imposto_pct = c5.number_input("Imposto sobre a venda (%)", min_value=0.0, max_value=100.0,
                                       value=float(imposto_padrao), step=0.5, format="%.2f")
        outras_taxas_pct = c6.number_input("Outras taxas / Ads (%)", min_value=0.0, max_value=100.0,
                                            value=float(outras_padrao), step=0.5, format="%.2f")

        margem_pct = st.slider("Margem de lucro desejada (%)", min_value=0.0, max_value=90.0,
                                value=float(margem_padrao), step=1.0)

        calcular = st.form_submit_button("🧮 Calcular preço de venda", use_container_width=True)

    if calcular:
        if custo_produto <= 0:
            st.error("Informe um custo de produto maior que zero.")
            return

        cpf = tipo_vendedor == "CPF"
        resultado = calcular_precificacao(
            custo_produto, custo_embalagem, custo_frete, cpf,
            imposto_pct, outras_taxas_pct, margem_pct, tiers, cpf_taxa_extra,
        )
        resultado_min = calcular_precificacao(
            custo_produto, custo_embalagem, custo_frete, cpf,
            imposto_pct, outras_taxas_pct, 0.0, tiers, cpf_taxa_extra,
        )

        preco = resultado["preco"]
        if preco is None:
            st.error(
                "Não foi possível calcular um preço viável com esses parâmetros — a soma de "
                "comissão, impostos, taxas e margem desejada ultrapassa 100% do preço de venda. "
                "Reduza a margem ou os custos percentuais."
            )
            return

        tier = resultado["tier"]
        detalhes = detalhar_precificacao(
            preco, tier, custo_produto, custo_embalagem, custo_frete,
            cpf, cpf_taxa_extra, imposto_pct, outras_taxas_pct,
        )
        preco_minimo = resultado_min["preco"]

        if resultado.get("aproximado"):
            st.markdown(
                "<div class='at-note'>⚠️ O preço calculado é uma aproximação: não convergiu "
                "exatamente dentro de nenhuma faixa cadastrada de comissão. Revise as faixas em "
                "<b>Configurações</b> se o resultado parecer inconsistente.</div>",
                unsafe_allow_html=True,
            )
            st.markdown("")

        col_preco, col_detalhe = st.columns([1, 1.4])
        with col_preco:
            st.markdown(
                f"""<div class='at-price-card'>
                        <div class='at-price-label'>PREÇO DE VENDA SUGERIDO</div>
                        <div class='at-price-value'>{formatar_moeda(preco)}</div>
                        <div style='margin-top:10px;color:#D8D8D2;font-size:0.85rem;'>
                            Faixa aplicada: comissão {formatar_pct(tier['comissao_pct'])} ·
                            preço mínimo (sem margem): {formatar_moeda(preco_minimo)}
                        </div>
                    </div>""",
                unsafe_allow_html=True,
            )
            st.markdown("")
            m1, m2 = st.columns(2)
            m1.metric("Lucro líquido por unidade", formatar_moeda(detalhes["lucro_liquido"]))
            m2.metric("Margem real", formatar_pct(detalhes["margem_real_pct"]))

        with col_detalhe:
            st.markdown("##### Composição do preço")
            linhas = [
                ("Custo do produto", custo_produto),
                ("Custo de embalagem", custo_embalagem),
                ("Frete adicional", custo_frete),
                ("Taxa extra (vendedor CPF)", detalhes["cpf_valor"]),
                (f"Comissão Shopee ({formatar_pct(tier['comissao_pct'])})", detalhes["comissao_valor"]),
                ("Taxa fixa por item", detalhes["taxa_fixa_valor"]),
                (f"Impostos ({formatar_pct(imposto_pct)})", detalhes["imposto_valor"]),
                (f"Outras taxas/Ads ({formatar_pct(outras_taxas_pct)})", detalhes["outras_valor"]),
                ("Lucro líquido (margem real)", detalhes["lucro_liquido"]),
            ]
            df_linhas = pd.DataFrame(linhas, columns=["Item", "Valor (R$)"])
            df_linhas["Valor (R$)"] = df_linhas["Valor (R$)"].apply(formatar_moeda)
            st.dataframe(df_linhas, use_container_width=True, hide_index=True)

        st.session_state["ultimo_calculo"] = {
            "produto_id": int(produto_selecionado["id"]) if produto_selecionado is not None else None,
            "produto_nome": (produto_selecionado["nome"] if produto_selecionado is not None
                              else escolha_produto if escolha_produto != "— Preenchimento manual —" else "Produto avulso"),
            "produto_sku": produto_selecionado["sku"] if produto_selecionado is not None else None,
            "custo_produto": custo_produto, "custo_embalagem": custo_embalagem, "custo_frete": custo_frete,
            "tipo_vendedor": tipo_vendedor, "faixa_comissao_pct": tier["comissao_pct"],
            "faixa_taxa_fixa": detalhes["taxa_fixa_valor"], "imposto_pct": imposto_pct,
            "outras_taxas_pct": outras_taxas_pct, "margem_desejada_pct": margem_pct,
            "preco_sugerido": preco, "preco_minimo": preco_minimo,
            "lucro_liquido": detalhes["lucro_liquido"], "margem_real_pct": detalhes["margem_real_pct"],
            "calculado_por": usuario["nome"],
        }

    if st.session_state.get("ultimo_calculo"):
        nome_produto_atual = st.session_state["ultimo_calculo"]["produto_nome"]
        if nome_produto_atual == "Produto avulso" or produto_selecionado is None:
            nome_manual = st.text_input(
                "Nome/identificação do item para salvar no histórico",
                value=nome_produto_atual if nome_produto_atual != "Produto avulso" else "",
                placeholder="Ex: Kit toalhas 3 peças",
            )
            st.session_state["ultimo_calculo"]["produto_nome"] = nome_manual or "Produto avulso"

        if st.button("💾 Salvar este cálculo no histórico", use_container_width=True):
            salvar_historico(st.session_state["ultimo_calculo"])
            st.success("Cálculo salvo no histórico com sucesso!")
            st.session_state["ultimo_calculo"] = None
            st.rerun()


# =====================================================================
# ABA: HISTÓRICO
# =====================================================================
def historico_tab():
    st.subheader("Histórico de precificações")

    historico = listar_historico()
    if historico.empty:
        st.info("Nenhum cálculo salvo ainda. Use a aba **Precificação** para começar.")
        return

    c1, c2 = st.columns(2)
    produtos_hist = ["Todos"] + sorted(historico["produto_nome"].dropna().unique().tolist())
    filtro_produto = c1.selectbox("Filtrar por produto", produtos_hist)
    usuarios_hist = ["Todos"] + sorted(historico["calculado_por"].dropna().unique().tolist())
    filtro_usuario = c2.selectbox("Filtrar por responsável", usuarios_hist)

    filtrado = historico.copy()
    if filtro_produto != "Todos":
        filtrado = filtrado[filtrado["produto_nome"] == filtro_produto]
    if filtro_usuario != "Todos":
        filtrado = filtrado[filtrado["calculado_por"] == filtro_usuario]

    tabela = filtrado[[
        "produto_nome", "tipo_vendedor", "preco_sugerido", "preco_minimo",
        "margem_real_pct", "lucro_liquido", "calculado_por", "calculado_em",
    ]].copy()
    tabela["preco_sugerido"] = tabela["preco_sugerido"].apply(formatar_moeda)
    tabela["preco_minimo"] = tabela["preco_minimo"].apply(formatar_moeda)
    tabela["margem_real_pct"] = tabela["margem_real_pct"].apply(formatar_pct)
    tabela["lucro_liquido"] = tabela["lucro_liquido"].apply(formatar_moeda)
    tabela["calculado_em"] = tabela["calculado_em"].apply(formatar_data)
    tabela.columns = ["Produto", "Vendedor", "Preço sugerido", "Preço mínimo", "Margem real",
                       "Lucro líquido", "Responsável", "Quando"]
    st.dataframe(tabela, use_container_width=True, hide_index=True)

    csv_buffer = io.StringIO()
    filtrado.to_csv(csv_buffer, index=False)
    st.download_button(
        "⬇️ Exportar histórico (CSV)", csv_buffer.getvalue(),
        file_name="historico_precificacao_alpha_textil.csv", mime="text/csv",
    )

    with st.expander("Excluir um registro do histórico"):
        opcoes_hist = {
            f"#{row.id} · {row.produto_nome} · {formatar_moeda(row.preco_sugerido)} · {formatar_data(row.calculado_em)}": row.id
            for row in filtrado.itertuples()
        }
        if opcoes_hist:
            escolha = st.selectbox("Selecione o registro", list(opcoes_hist.keys()))
            if st.button("🗑️ Excluir registro selecionado", type="secondary"):
                excluir_historico(opcoes_hist[escolha])
                st.success("Registro excluído.")
                st.rerun()


# =====================================================================
# ABA: CONFIGURAÇÕES
# =====================================================================
def configuracoes_tab(usuario):
    st.subheader("Configurações de taxas e equipe")

    st.markdown(
        "<div class='at-note'>Os valores abaixo refletem a estrutura de comissão da Shopee "
        "escalonada por faixa de preço (vigente desde 01/03/2026). Ajuste sempre que a Shopee "
        "atualizar as taxas no Seller Centre.</div>",
        unsafe_allow_html=True,
    )
    st.markdown("")

    tiers = get_config("fee_tiers", FEE_TIERS_PADRAO)
    df_tiers = pd.DataFrame(tiers)
    df_tiers = df_tiers.rename(columns={
        "min": "Faixa mínima (R$)", "max": "Faixa máxima (R$)",
        "comissao_pct": "Comissão (%)", "taxa_fixa": "Taxa fixa",
        "taxa_fixa_pct": "Taxa fixa é % do preço?",
    })

    st.markdown("##### Faixas de comissão e taxa fixa")
    st.caption(
        "Marque “Taxa fixa é % do preço?” para faixas em que a Shopee cobra um percentual "
        "(ex.: 50% do valor para itens abaixo de R$ 8,00) em vez de um valor fixo em reais. "
        "Para a faixa mais alta, use um valor grande em “Faixa máxima” (ex.: 999999,99) para representar “sem limite”."
    )
    df_editado = st.data_editor(
        df_tiers, num_rows="dynamic", use_container_width=True, hide_index=True,
        column_config={
            "Faixa mínima (R$)": st.column_config.NumberColumn(format="%.2f"),
            "Faixa máxima (R$)": st.column_config.NumberColumn(format="%.2f"),
            "Comissão (%)": st.column_config.NumberColumn(format="%.1f"),
            "Taxa fixa": st.column_config.NumberColumn(format="%.2f"),
            "Taxa fixa é % do preço?": st.column_config.CheckboxColumn(),
        },
    )

    st.markdown("##### Parâmetros padrão da calculadora")
    c1, c2, c3 = st.columns(3)
    imposto_pct = c1.number_input("Imposto sobre venda padrão (%)", min_value=0.0, max_value=100.0,
                                   value=float(get_config("imposto_pct", 6.0)), step=0.5)
    outras_taxas_pct = c2.number_input("Outras taxas/Ads padrão (%)", min_value=0.0, max_value=100.0,
                                        value=float(get_config("outras_taxas_pct", 0.0)), step=0.5)
    margem_padrao_pct = c3.number_input("Margem de lucro padrão (%)", min_value=0.0, max_value=90.0,
                                         value=float(get_config("margem_padrao_pct", 30.0)), step=1.0)
    cpf_taxa_extra = st.number_input(
        "Taxa fixa extra para vendedor Pessoa Física — CPF (R$ por item)",
        min_value=0.0, value=float(get_config("cpf_taxa_extra", 3.0)), step=0.5,
    )

    col_salvar, col_restaurar = st.columns(2)
    if col_salvar.button("💾 Salvar configurações", use_container_width=True):
        try:
            novos_tiers = df_editado.rename(columns={
                "Faixa mínima (R$)": "min", "Faixa máxima (R$)": "max",
                "Comissão (%)": "comissao_pct", "Taxa fixa": "taxa_fixa",
                "Taxa fixa é % do preço?": "taxa_fixa_pct",
            }).dropna(subset=["min", "max", "comissao_pct", "taxa_fixa"]).to_dict("records")
            set_config("fee_tiers", novos_tiers)
            set_config("imposto_pct", imposto_pct)
            set_config("outras_taxas_pct", outras_taxas_pct)
            set_config("margem_padrao_pct", margem_padrao_pct)
            set_config("cpf_taxa_extra", cpf_taxa_extra)
            st.success("Configurações salvas com sucesso!")
            st.rerun()
        except Exception as exc:  # noqa: BLE001
            st.error(f"Não foi possível salvar: verifique a tabela de faixas. ({exc})")

    if col_restaurar.button("↩️ Restaurar valores padrão", use_container_width=True, type="secondary"):
        for chave, valor in CONFIG_PADRAO.items():
            set_config(chave, valor)
        st.success("Valores padrão restaurados.")
        st.rerun()

    st.markdown("---")
    st.markdown("##### Equipe Alpha Têxtil")
    st.caption("Todos os membros têm acesso completo a todas as ferramentas do sistema.")
    usuarios_df = listar_usuarios()
    tabela_usuarios = usuarios_df.copy()
    tabela_usuarios["criado_em"] = tabela_usuarios["criado_em"].apply(formatar_data)
    tabela_usuarios = tabela_usuarios.rename(columns={
        "nome": "Nome", "email": "E-mail", "criado_em": "Cadastrado em",
    })[["Nome", "E-mail", "Cadastrado em"]]
    st.dataframe(tabela_usuarios, use_container_width=True, hide_index=True)

    with st.expander("Remover um membro da equipe"):
        if len(usuarios_df) <= 1:
            st.info("Não é possível remover o único usuário cadastrado no sistema.")
        else:
            opcoes_usuarios = {
                f"{row.nome} ({row.email})": row.id
                for row in usuarios_df.itertuples()
                if row.email != usuario["email"]
            }
            if opcoes_usuarios:
                escolha = st.selectbox("Selecione o membro", list(opcoes_usuarios.keys()))
                if st.button("🗑️ Remover membro selecionado", type="secondary"):
                    excluir_usuario(opcoes_usuarios[escolha])
                    st.success("Membro removido da equipe.")
                    st.rerun()
            else:
                st.info("Você é o único outro membro além de si mesmo — nada para remover aqui.")


# =====================================================================
# APLICATIVO PRINCIPAL (pós-login)
# =====================================================================
def app_principal():
    aplicar_estilo()
    usuario = st.session_state.usuario

    with st.sidebar:
        st.markdown("<div class='at-logo'>🧵 ALPHA TÊXTIL</div>", unsafe_allow_html=True)
        st.markdown("<div class='at-logo-sub'>GESTÃO SHOPEE</div>", unsafe_allow_html=True)
        st.markdown("")
        st.markdown(f"Olá, **{usuario['nome']}** 👋")
        st.caption(usuario["email"])
        st.markdown("<span class='at-chip'>Acesso completo</span>", unsafe_allow_html=True)
        st.markdown("---")
        total_usuarios = len(listar_usuarios())
        total_produtos = len(listar_produtos())
        st.metric("Membros da equipe", total_usuarios)
        st.metric("Produtos cadastrados", total_produtos)
        st.markdown("---")
        if st.button("🚪 Sair", use_container_width=True, type="secondary"):
            del st.session_state.usuario
            st.session_state.pop("ultimo_calculo", None)
            st.rerun()

    st.markdown("## 🧵 Gerenciador de Precificação e Gestão")
    st.caption("Alpha Têxtil · Produtos vendidos na Shopee")

    aba_dash, aba_produtos, aba_calc, aba_hist, aba_config = st.tabs([
        "📊 Dashboard", "📦 Produtos", "💰 Precificação", "🕓 Histórico", "⚙️ Configurações",
    ])

    with aba_dash:
        dashboard_tab()
    with aba_produtos:
        produtos_tab(usuario)
    with aba_calc:
        precificacao_tab(usuario)
    with aba_hist:
        historico_tab()
    with aba_config:
        configuracoes_tab(usuario)


# =====================================================================
# PONTO DE ENTRADA
# =====================================================================
def main():
    init_db()
    if "usuario" not in st.session_state:
        st.session_state.usuario = None
    if st.session_state.usuario is None:
        tela_login()
    else:
        app_principal()


if __name__ == "__main__":
    main()
