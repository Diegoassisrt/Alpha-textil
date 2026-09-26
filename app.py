# -*- coding: utf-8 -*-
"""
Alpha Têxtil - Gerenciador Profissional de Precificação e Gestão (Shopee)
Aplicativo único em Streamlit.

Como rodar:
    pip install streamlit pandas plotly
    streamlit run app.py

Login padrão:
    usuário: admin@alphatextil.com.br
    senha:   alpha2026
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ======================================================================================
# CONFIGURAÇÃO DA PÁGINA
# ======================================================================================
st.set_page_config(
    page_title="Alpha Têxtil | Precificação Shopee",
    page_icon="🧡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ======================================================================================
# IDENTIDADE VISUAL - DARK MODE PRETO & LARANJA (SEM AZUL)
# ======================================================================================
PRETO_FUNDO = "#0A0A0A"
PRETO_CARD = "#161616"
PRETO_CARD_BORDA = "#262626"
LARANJA = "#FF5A00"
LARANJA_CLARO = "#FF8A3D"
TEXTO_CLARO = "#F2F2F2"
TEXTO_CINZA = "#A3A3A3"

CUSTOM_CSS = f"""
<style>
    /* fundo geral */
    .stApp {{
        background-color: {PRETO_FUNDO};
        color: {TEXTO_CLARO};
    }}
    #MainMenu, footer, header {{visibility: hidden;}}

    h1, h2, h3, h4, h5, h6 {{
        color: {TEXTO_CLARO} !important;
        font-family: 'Segoe UI', sans-serif;
    }}
    p, span, label, div {{
        color: {TEXTO_CLARO};
    }}

    /* Título com gradiente laranja, remetendo à logo */
    .alpha-title {{
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(90deg, {LARANJA_CLARO} 0%, {LARANJA} 60%, #B33E00 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }}
    .alpha-subtitle {{
        color: {TEXTO_CINZA};
        font-size: 0.95rem;
        margin-top: -10px;
    }}

    /* Cards de KPI */
    .kpi-card {{
        background-color: {PRETO_CARD};
        border: 1px solid {PRETO_CARD_BORDA};
        border-left: 4px solid {LARANJA};
        border-radius: 10px;
        padding: 18px 20px;
        margin-bottom: 8px;
    }}
    .kpi-label {{
        color: {TEXTO_CINZA};
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }}
    .kpi-value {{
        color: {TEXTO_CLARO};
        font-size: 1.7rem;
        font-weight: 700;
    }}
    .kpi-value-orange {{
        color: {LARANJA};
        font-size: 1.9rem;
        font-weight: 800;
    }}

    /* Botões */
    .stButton>button {{
        background-color: {LARANJA};
        color: #0A0A0A;
        font-weight: 700;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.2rem;
        transition: 0.2s;
    }}
    .stButton>button:hover {{
        background-color: {LARANJA_CLARO};
        color: #000000;
    }}

    /* Inputs */
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div {{
        background-color: {PRETO_CARD} !important;
        color: {TEXTO_CLARO} !important;
        border: 1px solid {PRETO_CARD_BORDA} !important;
        border-radius: 6px !important;
    }}

    /* Abas */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 4px;
        background-color: transparent;
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: {PRETO_CARD};
        border-radius: 8px 8px 0 0;
        color: {TEXTO_CINZA};
        padding: 10px 18px;
        font-weight: 600;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {LARANJA} !important;
        color: #0A0A0A !important;
    }}

    /* Tabelas */
    .stDataFrame {{
        border: 1px solid {PRETO_CARD_BORDA};
        border-radius: 8px;
    }}

    /* Cartão genérico de seção */
    .section-card {{
        background-color: {PRETO_CARD};
        border: 1px solid {PRETO_CARD_BORDA};
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 16px;
    }}

    hr {{
        border-color: {PRETO_CARD_BORDA};
    }}

    /* Login box */
    .login-box {{
        background-color: {PRETO_CARD};
        border: 1px solid {PRETO_CARD_BORDA};
        border-radius: 14px;
        padding: 40px;
        margin-top: 30px;
    }}

    div[data-testid="stMetricValue"] {{
        color: {LARANJA} !important;
    }}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Template Plotly customizado (preto + laranja, zero azul)
PLOTLY_TEMPLATE = go.layout.Template()
PLOTLY_TEMPLATE.layout = go.Layout(
    paper_bgcolor=PRETO_CARD,
    plot_bgcolor=PRETO_CARD,
    font=dict(color=TEXTO_CLARO),
    xaxis=dict(gridcolor=PRETO_CARD_BORDA, zerolinecolor=PRETO_CARD_BORDA),
    yaxis=dict(gridcolor=PRETO_CARD_BORDA, zerolinecolor=PRETO_CARD_BORDA),
    colorway=[LARANJA, "#B33E00", LARANJA_CLARO, "#7A2900"],
)

# ======================================================================================
# ESTADO DA SESSÃO
# ======================================================================================
def init_state():
    if "users" not in st.session_state:
        st.session_state.users = {"admin@alphatextil.com.br": "alpha2026"}
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "current_user" not in st.session_state:
        st.session_state.current_user = ""
    if "produtos" not in st.session_state:
        st.session_state.produtos = []  # [{sku, nome, custo_fab, margem_desejada}]
    if "embalagens" not in st.session_state:
        st.session_state.embalagens = []  # [{item, valor}]
    if "custos_fixos" not in st.session_state:
        st.session_state.custos_fixos = []  # [{despesa, valor}]


init_state()

# ======================================================================================
# REGRAS DE NEGÓCIO - TAXAS SHOPEE E PRECIFICAÇÃO
# ======================================================================================
FAIXAS_SHOPEE = [
    (0.0, 80.0, 0.20, 4.50),
    (80.0, 100.0, 0.14, 16.00),
    (100.0, 200.0, 0.14, 20.00),
    (200.0, float("inf"), 0.14, 26.00),
]


def taxa_shopee(preco: float):
    """Retorna (comissao_pct, taxa_fixa) para um preço de venda praticado."""
    if preco < 80:
        return 0.20, 4.50
    elif preco < 100:
        return 0.14, 16.00
    elif preco < 200:
        return 0.14, 20.00
    else:
        return 0.14, 26.00


def calcular_preco_sugerido(custo_total: float, margem_desejada_pct: float):
    """
    Cálculo 'por dentro': encontra o preço de venda que, após descontar a
    comissão e a taxa fixa da faixa correspondente da Shopee, ainda entrega
    exatamente a margem líquida desejada sobre o preço de venda.

        Preço = (Custo + TaxaFixa) / (1 - Margem - Comissão)

    Testa cada faixa de taxa e valida se o preço resultante realmente cai
    dentro dos limites daquela faixa (pois a comissão muda conforme o preço).
    """
    margem = margem_desejada_pct / 100.0
    candidatos = []
    for lo, hi, comissao, fee in FAIXAS_SHOPEE:
        denom = 1 - margem - comissao
        if denom <= 0:
            continue
        preco = (custo_total + fee) / denom
        valido = (preco >= lo) and (preco < hi)
        candidatos.append((valido, preco, comissao, fee, lo, hi))

    validos = [c for c in candidatos if c[0]]
    if validos:
        _, preco, comissao, fee, _, _ = validos[0]
        return preco, comissao, fee

    # Fallback de segurança: nenhuma faixa fechou perfeitamente (raro) ->
    # escolhe o candidato mais próximo do seu próprio intervalo.
    if not candidatos:
        return custo_total, 0.20, 4.50

    melhor = min(
        candidatos,
        key=lambda c: (c[1] - c[4]) if c[1] < c[4] else (c[1] - c[5] if c[5] != float("inf") else 0),
    )
    return melhor[1], melhor[2], melhor[3]


def get_total_embalagem() -> float:
    return sum(item["valor"] for item in st.session_state.embalagens)


def get_total_fixo() -> float:
    return sum(item["valor"] for item in st.session_state.custos_fixos)


def get_rateio_fixo() -> float:
    n = len(st.session_state.produtos)
    if n == 0:
        return 0.0
    return get_total_fixo() / n


def build_dataframe_produtos() -> pd.DataFrame:
    embalagem_total = get_total_embalagem()
    rateio = get_rateio_fixo()
    rows = []
    for p in st.session_state.produtos:
        custo_total = p["custo_fab"] + embalagem_total + rateio
        preco_sug, comissao, fee = calcular_preco_sugerido(custo_total, p["margem_desejada"])
        taxa_valor = preco_sug * comissao + fee
        lucro = preco_sug - taxa_valor - custo_total
        margem_real = (lucro / preco_sug * 100) if preco_sug > 0 else 0.0
        rows.append(
            {
                "SKU": p["sku"],
                "Nome": p["nome"],
                "Custo Fabricação (R$)": round(p["custo_fab"], 2),
                "Embalagem (R$)": round(embalagem_total, 2),
                "Rateio Fixo (R$)": round(rateio, 2),
                "Custo Total (R$)": round(custo_total, 2),
                "Comissão (%)": round(comissao * 100, 1),
                "Taxa Fixa (R$)": round(fee, 2),
                "Taxa Shopee Total (R$)": round(taxa_valor, 2),
                "Preço Sugerido (R$)": round(preco_sug, 2),
                "Lucro Líquido (R$)": round(lucro, 2),
                "Margem Real (%)": round(margem_real, 2),
                "Margem Desejada (%)": p["margem_desejada"],
            }
        )
    return pd.DataFrame(rows)


def fmt_moeda(v: float) -> str:
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# ======================================================================================
# TELA DE LOGIN / CADASTRO
# ======================================================================================
def tela_login():
    col_a, col_b, col_c = st.columns([1, 1.4, 1])
    with col_b:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            "<div class='alpha-title' style='text-align:center;'>ALPHA TÊXTIL</div>"
            "<div class='alpha-subtitle' style='text-align:center;'>Gestão de Precificação & Taxas Shopee</div>",
            unsafe_allow_html=True,
        )
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)

        aba_login, aba_cadastro = st.tabs(["🔐 Entrar", "🆕 Cadastrar membro"])

        with aba_login:
            email = st.text_input("E-mail", key="login_email", placeholder="seuemail@alphatextil.com.br")
            senha = st.text_input("Senha", key="login_senha", type="password", placeholder="••••••••")
            if st.button("Entrar no sistema", use_container_width=True):
                usuarios = st.session_state.users
                if email in usuarios and usuarios[email] == senha:
                    st.session_state.logged_in = True
                    st.session_state.current_user = email
                    st.rerun()
                else:
                    st.error("E-mail ou senha inválidos.")
            st.caption("Usuário padrão: admin@alphatextil.com.br / senha: alpha2026")

        with aba_cadastro:
            novo_email = st.text_input("E-mail do novo membro", key="cad_email")
            nova_senha = st.text_input("Crie uma senha", key="cad_senha", type="password")
            confirmar = st.text_input("Confirme a senha", key="cad_confirma", type="password")
            if st.button("Cadastrar novo membro", use_container_width=True):
                if not novo_email or not nova_senha:
                    st.error("Preencha e-mail e senha.")
                elif novo_email in st.session_state.users:
                    st.error("Este e-mail já está cadastrado.")
                elif nova_senha != confirmar:
                    st.error("As senhas não conferem.")
                else:
                    st.session_state.users[novo_email] = nova_senha
                    st.success("Membro cadastrado! Vá até a aba Entrar para fazer login.")

        st.markdown("</div>", unsafe_allow_html=True)


# ======================================================================================
# ABA 1 - DASHBOARD GERAL
# ======================================================================================
def aba_dashboard():
    df = build_dataframe_produtos()

    total_pecas = len(df)
    faturamento_bruto = df["Preço Sugerido (R$)"].sum() if not df.empty else 0.0
    lucro_liquido_total = df["Lucro Líquido (R$)"].sum() if not df.empty else 0.0
    custo_total_producao = df["Custo Total (R$)"].sum() if not df.empty else 0.0
    taxas_totais = df["Taxa Shopee Total (R$)"].sum() if not df.empty else 0.0
    margem_media = df["Margem Real (%)"].mean() if not df.empty else 0.0

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f"<div class='kpi-card'><div class='kpi-label'>Peças Cadastradas</div>"
            f"<div class='kpi-value'>{total_pecas}</div></div>",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"<div class='kpi-card'><div class='kpi-label'>Faturamento Bruto Estimado</div>"
            f"<div class='kpi-value'>{fmt_moeda(faturamento_bruto)}</div></div>",
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"<div class='kpi-card'><div class='kpi-label'>Lucro Líquido Final</div>"
            f"<div class='kpi-value-orange'>{fmt_moeda(lucro_liquido_total)}</div></div>",
            unsafe_allow_html=True,
        )

    c4, c5, c6 = st.columns(3)
    with c4:
        st.markdown(
            f"<div class='kpi-card'><div class='kpi-label'>Margem Média Geral</div>"
            f"<div class='kpi-value'>{margem_media:.2f}%</div></div>",
            unsafe_allow_html=True,
        )
    with c5:
        st.markdown(
            f"<div class='kpi-card'><div class='kpi-label'>Custo Total de Produção</div>"
            f"<div class='kpi-value'>{fmt_moeda(custo_total_producao)}</div></div>",
            unsafe_allow_html=True,
        )
    with c6:
        st.markdown(
            f"<div class='kpi-card'><div class='kpi-label'>Total Estimado em Taxas Shopee</div>"
            f"<div class='kpi-value'>{fmt_moeda(taxas_totais)}</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    if df.empty:
        st.info("Cadastre produtos na aba **Catálogo e Precificação** para visualizar os gráficos e a tabela de margem.")
        return

    col_graf, col_tab = st.columns([1.3, 1])
    with col_graf:
        st.markdown("#### 📊 Margem Real por Peça")
        fig = go.Figure()
        cores = [LARANJA if v >= 0 else "#3A3A3A" for v in df["Margem Real (%)"]]
        fig.add_trace(
            go.Bar(
                x=df["Nome"],
                y=df["Margem Real (%)"],
                marker_color=cores,
                marker_line_color="#000000",
                marker_line_width=1,
                text=df["Margem Real (%)"].map(lambda v: f"{v:.1f}%"),
                textposition="outside",
            )
        )
        fig.update_layout(
            template=PLOTLY_TEMPLATE,
            yaxis_title="Margem Real (%)",
            xaxis_title="",
            height=420,
            margin=dict(t=20, b=40),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_tab:
        st.markdown("#### 🧾 Resumo por Peça")
        st.dataframe(
            df[["SKU", "Nome", "Preço Sugerido (R$)", "Lucro Líquido (R$)", "Margem Real (%)"]],
            use_container_width=True,
            hide_index=True,
            height=420,
        )


# ======================================================================================
# ABA 2 - CUSTOS E RATEIO AUTOMÁTICO
# ======================================================================================
def aba_custos():
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("#### 📦 Custos de Embalagem")
        st.caption("Itens usados no envio de cada peça (caixa, fita, etiqueta, plástico, etc).")
        with st.form("form_embalagem", clear_on_submit=True):
            ce1, ce2 = st.columns([2, 1])
            item = ce1.text_input("Item")
            valor = ce2.number_input("Valor (R$)", min_value=0.0, step=0.10, format="%.2f")
            add = st.form_submit_button("➕ Adicionar item de embalagem")
            if add:
                if item.strip() == "":
                    st.error("Informe o nome do item.")
                else:
                    st.session_state.embalagens.append({"item": item.strip(), "valor": valor})
                    st.success(f"'{item}' adicionado.")

        if st.session_state.embalagens:
            df_emb = pd.DataFrame(st.session_state.embalagens)
            df_emb.columns = ["Item", "Valor (R$)"]
            st.dataframe(df_emb, use_container_width=True, hide_index=True)

            del_idx = st.selectbox(
                "Remover item de embalagem",
                options=list(range(len(st.session_state.embalagens))),
                format_func=lambda i: st.session_state.embalagens[i]["item"],
                key="del_emb",
            )
            if st.button("🗑️ Remover item selecionado", key="btn_del_emb"):
                st.session_state.embalagens.pop(del_idx)
                st.rerun()

            st.markdown(
                f"<div class='kpi-card'><div class='kpi-label'>Custo Total de Embalagem (por peça)</div>"
                f"<div class='kpi-value-orange'>{fmt_moeda(get_total_embalagem())}</div></div>",
                unsafe_allow_html=True,
            )
        else:
            st.info("Nenhum item de embalagem cadastrado ainda.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("#### 🏭 Custos Fixos Mensais")
        st.caption("Despesas mensais do negócio (MEI, internet, energia, aluguel, etc).")
        with st.form("form_fixo", clear_on_submit=True):
            cf1, cf2 = st.columns([2, 1])
            despesa = cf1.text_input("Despesa")
            valor_f = cf2.number_input("Valor mensal (R$)", min_value=0.0, step=1.0, format="%.2f")
            add_f = st.form_submit_button("➕ Adicionar custo fixo")
            if add_f:
                if despesa.strip() == "":
                    st.error("Informe o nome da despesa.")
                else:
                    st.session_state.custos_fixos.append({"despesa": despesa.strip(), "valor": valor_f})
                    st.success(f"'{despesa}' adicionado.")

        if st.session_state.custos_fixos:
            df_fixo = pd.DataFrame(st.session_state.custos_fixos)
            df_fixo.columns = ["Despesa", "Valor Mensal (R$)"]
            st.dataframe(df_fixo, use_container_width=True, hide_index=True)

            del_idx_f = st.selectbox(
                "Remover custo fixo",
                options=list(range(len(st.session_state.custos_fixos))),
                format_func=lambda i: st.session_state.custos_fixos[i]["despesa"],
                key="del_fixo",
            )
            if st.button("🗑️ Remover custo selecionado", key="btn_del_fixo"):
                st.session_state.custos_fixos.pop(del_idx_f)
                st.rerun()

            n_produtos = len(st.session_state.produtos)
            k1, k2, k3 = st.columns(3)
            with k1:
                st.markdown(
                    f"<div class='kpi-card'><div class='kpi-label'>Total Fixo Mensal</div>"
                    f"<div class='kpi-value'>{fmt_moeda(get_total_fixo())}</div></div>",
                    unsafe_allow_html=True,
                )
            with k2:
                st.markdown(
                    f"<div class='kpi-card'><div class='kpi-label'>Produtos no Catálogo</div>"
                    f"<div class='kpi-value'>{n_produtos}</div></div>",
                    unsafe_allow_html=True,
                )
            with k3:
                st.markdown(
                    f"<div class='kpi-card'><div class='kpi-label'>Rateio Fixo por Peça</div>"
                    f"<div class='kpi-value-orange'>{fmt_moeda(get_rateio_fixo())}</div></div>",
                    unsafe_allow_html=True,
                )
            if n_produtos == 0:
                st.warning("Cadastre produtos no Catálogo para que o rateio seja calculado automaticamente.")
        else:
            st.info("Nenhum custo fixo cadastrado ainda.")
        st.markdown("</div>", unsafe_allow_html=True)


# ======================================================================================
# ABA 3 - CATÁLOGO E PRECIFICAÇÃO
# ======================================================================================
def aba_catalogo():
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("#### 🧵 Cadastrar Nova Peça")
    with st.form("form_produto", clear_on_submit=True):
        p1, p2, p3, p4 = st.columns(4)
        sku = p1.text_input("SKU")
        nome = p2.text_input("Nome da Peça")
        custo_fab = p3.number_input("Custo de Fabricação (R$)", min_value=0.0, step=0.50, format="%.2f")
        margem = p4.number_input("Margem Desejada (%)", min_value=0.0, max_value=95.0, step=1.0, value=30.0)
        add_p = st.form_submit_button("➕ Adicionar peça ao catálogo")
        if add_p:
            if sku.strip() == "" or nome.strip() == "":
                st.error("Preencha SKU e Nome.")
            elif any(p["sku"] == sku.strip() for p in st.session_state.produtos):
                st.error("Já existe uma peça com esse SKU.")
            else:
                st.session_state.produtos.append(
                    {"sku": sku.strip(), "nome": nome.strip(), "custo_fab": custo_fab, "margem_desejada": margem}
                )
                st.success(f"Peça '{nome}' cadastrada.")
    st.markdown("</div>", unsafe_allow_html=True)

    if not st.session_state.produtos:
        st.info("Nenhuma peça cadastrada ainda.")
        return

    st.markdown("#### 💰 Tabela de Precificação Automática")
    st.caption(
        "Custo Total = Fabricação + Embalagem (rateada por peça) + Rateio de Custos Fixos. "
        "O Preço Sugerido usa cálculo 'por dentro', blindando sua margem desejada após os descontos da Shopee."
    )
    df = build_dataframe_produtos()
    st.dataframe(df, use_container_width=True, hide_index=True)

    del_idx_p = st.selectbox(
        "Remover peça do catálogo",
        options=list(range(len(st.session_state.produtos))),
        format_func=lambda i: f"{st.session_state.produtos[i]['sku']} - {st.session_state.produtos[i]['nome']}",
        key="del_prod",
    )
    if st.button("🗑️ Remover peça selecionada"):
        st.session_state.produtos.pop(del_idx_p)
        st.rerun()

    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("⬇️ Exportar tabela em CSV", data=csv, file_name="precificacao_alpha_textil.csv", mime="text/csv")


# ======================================================================================
# ABA 4 - REGRAS DE TAXAS SHOPEE
# ======================================================================================
def aba_regras():
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("#### 📋 Regras Automáticas de Taxas da Shopee")
    st.caption("Estas faixas são aplicadas automaticamente em todo o sistema (Catálogo e Simulador).")

    regras_df = pd.DataFrame(
        [
            {"Faixa de Preço": "Menor que R$ 80,00", "Comissão": "20%", "Taxa Fixa": "R$ 4,50"},
            {"Faixa de Preço": "De R$ 80,00 até R$ 99,99", "Comissão": "14%", "Taxa Fixa": "R$ 16,00"},
            {"Faixa de Preço": "De R$ 100,00 até R$ 199,99", "Comissão": "14%", "Taxa Fixa": "R$ 20,00"},
            {"Faixa de Preço": "A partir de R$ 200,00", "Comissão": "14%", "Taxa Fixa": "R$ 26,00"},
        ]
    )
    st.dataframe(regras_df, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("#### 🔎 Consulta Rápida de Taxa por Preço")
    preco_consulta = st.number_input("Digite um preço de venda (R$)", min_value=0.0, step=1.0, value=100.0, key="consulta_preco")
    comissao_c, fee_c = taxa_shopee(preco_consulta)
    valor_taxa_c = preco_consulta * comissao_c + fee_c
    q1, q2, q3 = st.columns(3)
    with q1:
        st.markdown(
            f"<div class='kpi-card'><div class='kpi-label'>Comissão Aplicada</div>"
            f"<div class='kpi-value'>{comissao_c*100:.0f}%</div></div>",
            unsafe_allow_html=True,
        )
    with q2:
        st.markdown(
            f"<div class='kpi-card'><div class='kpi-label'>Taxa Fixa</div>"
            f"<div class='kpi-value'>{fmt_moeda(fee_c)}</div></div>",
            unsafe_allow_html=True,
        )
    with q3:
        st.markdown(
            f"<div class='kpi-card'><div class='kpi-label'>Valor Total da Taxa</div>"
            f"<div class='kpi-value-orange'>{fmt_moeda(valor_taxa_c)}</div></div>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


# ======================================================================================
# ABA 5 - SIMULADOR DE PREÇO
# ======================================================================================
def aba_simulador():
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("#### 🧮 Simulador de Preço Praticado")
    st.caption("Informe o custo total da peça e um preço de venda que você pretende praticar (ou já pratica) para ver o resultado real.")

    s1, s2 = st.columns(2)
    custo_sim = s1.number_input("Custo Total do Produto (R$)", min_value=0.0, step=0.50, format="%.2f", key="sim_custo")
    preco_sim = s2.number_input("Preço de Venda Praticado (R$)", min_value=0.0, step=0.50, format="%.2f", key="sim_preco")

    if st.button("🔍 Simular"):
        comissao_s, fee_s = taxa_shopee(preco_sim)
        taxa_total_s = preco_sim * comissao_s + fee_s
        lucro_s = preco_sim - taxa_total_s - custo_sim
        margem_s = (lucro_s / preco_sim * 100) if preco_sim > 0 else 0.0

        st.markdown("<br>", unsafe_allow_html=True)
        r1, r2 = st.columns(2)
        with r1:
            st.markdown(
                f"<div class='kpi-card'><div class='kpi-label'>Comissão Shopee</div>"
                f"<div class='kpi-value'>{comissao_s*100:.0f}%</div></div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div class='kpi-card'><div class='kpi-label'>Taxa Fixa</div>"
                f"<div class='kpi-value'>{fmt_moeda(fee_s)}</div></div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div class='kpi-card'><div class='kpi-label'>Taxa Total Descontada</div>"
                f"<div class='kpi-value'>{fmt_moeda(taxa_total_s)}</div></div>",
                unsafe_allow_html=True,
            )
        with r2:
            cor_lucro = "kpi-value-orange" if lucro_s >= 0 else "kpi-value"
            st.markdown(
                f"<div class='kpi-card'><div class='kpi-label'>Lucro Líquido Estimado</div>"
                f"<div class='{cor_lucro}'>{fmt_moeda(lucro_s)}</div></div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div class='kpi-card'><div class='kpi-label'>Margem Real</div>"
                f"<div class='kpi-value-orange'>{margem_s:.2f}%</div></div>",
                unsafe_allow_html=True,
            )
            if lucro_s < 0:
                st.error("⚠️ Prejuízo nesse cenário: o preço não cobre o custo + taxas.")
            elif margem_s < 10:
                st.warning("Margem apertada (abaixo de 10%). Avalie reajustar o preço.")
            else:
                st.success("Cenário saudável. ✅")
    st.markdown("</div>", unsafe_allow_html=True)


# ======================================================================================
# APLICAÇÃO PRINCIPAL (PÓS-LOGIN)
# ======================================================================================
def app_principal():
    top1, top2 = st.columns([4, 1])
    with top1:
        st.markdown(
            "<div class='alpha-title'>ALPHA TÊXTIL</div>"
            "<div class='alpha-subtitle'>Gerenciador Profissional de Precificação e Gestão · Shopee</div>",
            unsafe_allow_html=True,
        )
    with top2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.caption(f"👤 {st.session_state.current_user}")
        if st.button("Sair", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.current_user = ""
            st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "📊 Dashboard Geral",
            "🏭 Custos e Rateio",
            "🧵 Catálogo e Precificação",
            "📋 Regras da Shopee",
            "🧮 Simulador de Preço",
        ]
    )
    with tab1:
        aba_dashboard()
    with tab2:
        aba_custos()
    with tab3:
        aba_catalogo()
    with tab4:
        aba_regras()
    with tab5:
        aba_simulador()


# ======================================================================================
# ROTEAMENTO
# ======================================================================================
if st.session_state.logged_in:
    app_principal()
else:
    tela_login()
