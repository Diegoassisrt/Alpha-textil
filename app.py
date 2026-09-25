# -*- coding: utf-8 -*-
"""
================================================================================
 ALPHA TÊXTIL - GERENCIADOR DE PRECIFICAÇÃO SHOPEE
================================================================================
Aplicativo web desenvolvido em Streamlit para gestão de precificação de
produtos vendidos na Shopee, com cálculo automático de taxas, rateio de
custos fixos, embalagem e margem de lucro.

Como executar:
    1. pip install -r requirements.txt
    2. streamlit run app.py

Login padrão:
    usuário: admin
    senha:   alpha2026
================================================================================
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==============================================================================
# 1. CONFIGURAÇÃO GERAL DA PÁGINA E IDENTIDADE VISUAL
# ==============================================================================

st.set_page_config(
    page_title="Alpha Têxtil | Gerenciador de Precificação",
    page_icon="🧵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Paleta de cores oficial da marca
COR_PRETO = "#000000"
COR_LARANJA = "#FF6600"
COR_LARANJA_ESCURO = "#CC5200"
COR_CINZA_CLARO = "#F5F5F5"
COR_BRANCO = "#FFFFFF"
COR_CINZA_TEXTO = "#333333"

# CSS customizado para forçar a identidade visual em toda a aplicação
CUSTOM_CSS = f"""
<style>
    /* Fundo geral */
    .stApp {{
        background-color: {COR_CINZA_CLARO};
    }}

    /* Cabeçalhos */
    h1, h2, h3 {{
        color: {COR_PRETO} !important;
        font-weight: 800 !important;
    }}

    /* Sidebar preta */
    section[data-testid="stSidebar"] {{
        background-color: {COR_PRETO};
    }}
    section[data-testid="stSidebar"] * {{
        color: {COR_BRANCO} !important;
    }}
    section[data-testid="stSidebar"] .stButton button {{
        background-color: {COR_LARANJA};
        color: {COR_PRETO} !important;
        border: none;
        font-weight: 700;
    }}

    /* Botões principais */
    .stButton button {{
        background-color: {COR_LARANJA};
        color: {COR_PRETO};
        font-weight: 700;
        border: none;
        border-radius: 6px;
        transition: 0.2s;
    }}
    .stButton button:hover {{
        background-color: {COR_LARANJA_ESCURO};
        color: {COR_BRANCO};
    }}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 6px;
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: {COR_BRANCO};
        border-radius: 6px 6px 0 0;
        padding: 8px 16px;
        border: 1px solid #ddd;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {COR_PRETO} !important;
        color: {COR_LARANJA} !important;
    }}

    /* Cards de métrica (KPI) */
    div[data-testid="stMetric"] {{
        background-color: {COR_BRANCO};
        border: 1px solid #e0e0e0;
        border-left: 6px solid {COR_LARANJA};
        border-radius: 8px;
        padding: 14px 18px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    }}
    div[data-testid="stMetricValue"] {{
        color: {COR_PRETO} !important;
        font-weight: 800 !important;
    }}
    div[data-testid="stMetricLabel"] {{
        color: {COR_CINZA_TEXTO} !important;
    }}

    /* Dataframes */
    .stDataFrame {{
        border: 1px solid #ddd;
        border-radius: 6px;
    }}

    /* Divisores */
    hr {{
        border-top: 2px solid {COR_LARANJA};
    }}

    /* Logo / título topo */
    .alpha-header {{
        background-color: {COR_PRETO};
        padding: 18px 24px;
        border-radius: 8px;
        margin-bottom: 18px;
        border-left: 8px solid {COR_LARANJA};
    }}
    .alpha-header h1 {{
        color: {COR_BRANCO} !important;
        margin: 0;
        font-size: 28px;
    }}
    .alpha-header span {{
        color: {COR_LARANJA};
    }}
    .alpha-header p {{
        color: #cccccc;
        margin: 0;
        font-size: 14px;
    }}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Paleta usada diretamente nos gráficos Plotly
PALETA_GRAFICO = [COR_LARANJA, COR_PRETO, "#FFA366", "#595959", "#FF8C33", "#8C8C8C"]


# ==============================================================================
# 2. CREDENCIAIS E CONTROLE DE LOGIN
# ==============================================================================

USUARIO_PADRAO = "admin"
SENHA_PADRAO = "alpha2026"


def tela_login():
    """Renderiza a tela de autenticação. Só libera o painel após login válido."""
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown(
            f"""
            <div style="text-align:center; margin-top:60px; margin-bottom:20px;">
                <h1 style="color:{COR_PRETO}; font-size:34px;">🧵 ALPHA <span style="color:{COR_LARANJA};">TÊXTIL</span></h1>
                <p style="color:{COR_CINZA_TEXTO};">Gerenciador de Precificação Shopee</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.form("form_login"):
            usuario = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            entrar = st.form_submit_button("Entrar", use_container_width=True)

            if entrar:
                if usuario == USUARIO_PADRAO and senha == SENHA_PADRAO:
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("Usuário ou senha inválidos. Tente novamente.")

        st.caption("Acesso restrito — Alpha Têxtil © 2026")


# ==============================================================================
# 3. ESTADO INICIAL DA APLICAÇÃO (BANCO DE DADOS EM MEMÓRIA)
# ==============================================================================

def inicializar_estado():
    """Garante que todas as chaves necessárias existam no session_state."""
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if "produtos" not in st.session_state:
        # Lista de dicionários representando cada produto cadastrado
        st.session_state.produtos = [
            {"codigo": "AT001", "nome": "Camiseta Básica Algodão", "categoria": "Camisetas",
             "custo_fabricacao": 18.50, "margem_desejada": 30.0},
            {"codigo": "AT002", "nome": "Moletom Canguru", "categoria": "Moletons",
             "custo_fabricacao": 45.00, "margem_desejada": 25.0},
            {"codigo": "AT003", "nome": "Legging Fitness", "categoria": "Fitness",
             "custo_fabricacao": 22.00, "margem_desejada": 35.0},
        ]

    if "embalagens" not in st.session_state:
        # Custos unitários de embalagem
        st.session_state.embalagens = {
            "Saco plástico": 0.35,
            "Saco de envio": 0.60,
            "Etiqueta": 0.15,
            "Fita": 0.10,
            "Tag": 0.20,
        }

    if "custos_fixos" not in st.session_state:
        # Lista de despesas mensais fixas
        st.session_state.custos_fixos = [
            {"nome": "MEI", "valor": 76.00},
            {"nome": "Internet", "valor": 100.00},
        ]


# ==============================================================================
# 4. REGRAS DE NEGÓCIO — TAXAS SHOPEE E PRECIFICAÇÃO
# ==============================================================================

# Faixas oficiais de comissão + taxa fixa da Shopee
FAIXAS_SHOPEE = [
    {"min": 0.00, "max": 79.99, "comissao": 0.20, "fixa": 4.50, "label": "Até R$ 79,99"},
    {"min": 80.00, "max": 99.99, "comissao": 0.14, "fixa": 16.00, "label": "R$ 80,00 a R$ 99,99"},
    {"min": 100.00, "max": 199.99, "comissao": 0.14, "fixa": 20.00, "label": "R$ 100,00 a R$ 199,99"},
    {"min": 200.00, "max": float("inf"), "comissao": 0.14, "fixa": 26.00, "label": "Acima de R$ 200,00"},
]


def obter_faixa_shopee(preco: float) -> dict:
    """Retorna a faixa de comissão da Shopee correspondente ao preço informado."""
    for faixa in FAIXAS_SHOPEE:
        if faixa["min"] <= preco <= faixa["max"]:
            return faixa
    return FAIXAS_SHOPEE[-1]


def calcular_taxa_shopee_reais(preco: float) -> float:
    """Calcula o valor em R$ descontado pela Shopee para um dado preço de venda."""
    faixa = obter_faixa_shopee(preco)
    return (preco * faixa["comissao"]) + faixa["fixa"]


def calcular_embalagem_total() -> float:
    """Soma todos os custos unitários de embalagem cadastrados."""
    return sum(st.session_state.embalagens.values())


def calcular_rateio_fixo_por_peca() -> float:
    """Divide o total de custos fixos mensais pela quantidade de produtos cadastrados."""
    total_fixo = sum(item["valor"] for item in st.session_state.custos_fixos)
    qtd_produtos = len(st.session_state.produtos)
    if qtd_produtos == 0:
        return 0.0
    return total_fixo / qtd_produtos


def calcular_preco_venda_sugerido(custo_total: float, margem_desejada_pct: float):
    """
    Calcula o preço de venda sugerido usando o cálculo matemático inverso "por dentro",
    garantindo que a margem de lucro desejada seja limpa após os descontos da Shopee.

        Preço = (Custo Total + Taxa Fixa) / (1 - % Taxa Shopee - % Margem Desejada)

    Como a faixa de taxa depende do próprio preço (é escalonada), testamos cada
    faixa e validamos se o preço resultante realmente pertence a ela.
    Retorna: (preco_sugerido, comissao_pct, taxa_fixa)
    """
    margem = margem_desejada_pct / 100
    candidatos_validos = []

    for faixa in FAIXAS_SHOPEE:
        denominador = 1 - faixa["comissao"] - margem
        if denominador <= 0:
            # Margem + comissão inviável matematicamente nesta faixa
            continue
        preco_calculado = (custo_total + faixa["fixa"]) / denominador
        if faixa["min"] <= preco_calculado <= faixa["max"]:
            candidatos_validos.append((preco_calculado, faixa["comissao"], faixa["fixa"]))

    if candidatos_validos:
        # Em caso de mais de uma faixa válida (raro), pega a de menor preço
        candidatos_validos.sort(key=lambda x: x[0])
        return candidatos_validos[0]

    # Fallback de segurança: usa a última faixa (acima de R$200) se nada bateu
    faixa = FAIXAS_SHOPEE[-1]
    denominador = max(1 - faixa["comissao"] - margem, 0.01)
    preco_calculado = (custo_total + faixa["fixa"]) / denominador
    return preco_calculado, faixa["comissao"], faixa["fixa"]


def montar_tabela_precificacao() -> pd.DataFrame:
    """Monta o DataFrame completo com todos os cálculos de custo, taxa e lucro por produto."""
    embalagem_unit = calcular_embalagem_total()
    rateio_fixo = calcular_rateio_fixo_por_peca()

    linhas = []
    for p in st.session_state.produtos:
        custo_total = p["custo_fabricacao"] + embalagem_unit + rateio_fixo

        preco_sugerido, comissao_pct, taxa_fixa = calcular_preco_venda_sugerido(
            custo_total, p["margem_desejada"]
        )

        taxa_shopee_reais = calcular_taxa_shopee_reais(preco_sugerido)
        lucro_liquido = preco_sugerido - custo_total - taxa_shopee_reais
        margem_real = (lucro_liquido / preco_sugerido * 100) if preco_sugerido > 0 else 0

        linhas.append({
            "Código": p["codigo"],
            "Produto": p["nome"],
            "Categoria": p["categoria"],
            "Custo Fabricação": p["custo_fabricacao"],
            "Embalagem": embalagem_unit,
            "Rateio Fixo": rateio_fixo,
            "Custo Total": custo_total,
            "Margem Desejada (%)": p["margem_desejada"],
            "Comissão Shopee (%)": comissao_pct * 100,
            "Taxa Fixa Shopee": taxa_fixa,
            "Taxa Shopee (R$)": taxa_shopee_reais,
            "Preço Venda Sugerido": preco_sugerido,
            "Lucro Líquido (R$)": lucro_liquido,
            "Margem Real (%)": margem_real,
        })

    return pd.DataFrame(linhas)


# ==============================================================================
# 5. PÁGINAS DO SISTEMA
# ==============================================================================

def formatar_moeda(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def pagina_dashboard():
    st.header("📊 Painel de Resultados")

    df = montar_tabela_precificacao()

    if df.empty:
        st.info("Nenhum produto cadastrado ainda. Vá até a aba **Produtos** para começar.")
        return

    total_pecas = len(df)
    faturamento_bruto = df["Preço Venda Sugerido"].sum()
    lucro_liquido_total = df["Lucro Líquido (R$)"].sum()
    margem_media = df["Margem Real (%)"].mean()
    custo_total_produtos = df["Custo Total"].sum()
    total_taxas_shopee = df["Taxa Shopee (R$)"].sum()

    # --- Linha 1 de KPIs ---
    c1, c2, c3 = st.columns(3)
    c1.metric("📦 Peças Cadastradas", f"{total_pecas}")
    c2.metric("💰 Faturamento Bruto Estimado", formatar_moeda(faturamento_bruto))
    c3.metric("🟧 Lucro Líquido Total", formatar_moeda(lucro_liquido_total))

    # --- Linha 2 de KPIs ---
    c4, c5, c6 = st.columns(3)
    c4.metric("📈 Margem Média de Lucro", f"{margem_media:.1f}%")
    c5.metric("🏭 Custo Total dos Produtos", formatar_moeda(custo_total_produtos))
    c6.metric("🛍️ Total de Taxas Shopee", formatar_moeda(total_taxas_shopee))

    st.markdown("---")

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Margem Real por Produto")
        fig1 = px.bar(
            df, x="Produto", y="Margem Real (%)", color="Produto",
            color_discrete_sequence=PALETA_GRAFICO, text_auto=".1f",
        )
        fig1.update_layout(
            plot_bgcolor=COR_BRANCO, paper_bgcolor=COR_BRANCO,
            font_color=COR_PRETO, showlegend=False,
        )
        fig1.update_traces(marker_line_color=COR_PRETO, marker_line_width=1)
        st.plotly_chart(fig1, use_container_width=True)

    with col_b:
        st.subheader("Lucro Líquido por Produto (R$)")
        fig2 = px.bar(
            df, x="Produto", y="Lucro Líquido (R$)", color="Produto",
            color_discrete_sequence=PALETA_GRAFICO, text_auto=".2f",
        )
        fig2.update_layout(
            plot_bgcolor=COR_BRANCO, paper_bgcolor=COR_BRANCO,
            font_color=COR_PRETO, showlegend=False,
        )
        fig2.update_traces(marker_line_color=COR_PRETO, marker_line_width=1)
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Composição: Custo x Taxa Shopee x Lucro")
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(name="Custo Total", x=df["Produto"], y=df["Custo Total"], marker_color=COR_PRETO))
    fig3.add_trace(go.Bar(name="Taxa Shopee", x=df["Produto"], y=df["Taxa Shopee (R$)"], marker_color="#8C8C8C"))
    fig3.add_trace(go.Bar(name="Lucro Líquido", x=df["Produto"], y=df["Lucro Líquido (R$)"], marker_color=COR_LARANJA))
    fig3.update_layout(
        barmode="stack", plot_bgcolor=COR_BRANCO, paper_bgcolor=COR_BRANCO,
        font_color=COR_PRETO, legend_title_text="",
    )
    st.plotly_chart(fig3, use_container_width=True)


def pagina_taxas_shopee():
    st.header("⚙️ Configuração de Taxas da Shopee")
    st.markdown(
        "O sistema aplica **automaticamente** a faixa de comissão correspondente "
        "ao preço de venda calculado de cada produto. Estas são as regras vigentes:"
    )

    df_faixas = pd.DataFrame([
        {
            "Faixa de Preço": f["label"],
            "Comissão (%)": f"{f['comissao']*100:.0f}%",
            "Taxa Fixa": formatar_moeda(f["fixa"]),
        }
        for f in FAIXAS_SHOPEE
    ])
    st.dataframe(df_faixas, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("🔎 Consulta rápida de faixa")
    preco_teste = st.number_input("Digite um preço para ver a faixa aplicada:", min_value=0.0, step=1.0, value=100.0)
    faixa = obter_faixa_shopee(preco_teste)
    taxa_reais = calcular_taxa_shopee_reais(preco_teste)
    c1, c2, c3 = st.columns(3)
    c1.metric("Faixa aplicada", faixa["label"])
    c2.metric("Comissão", f"{faixa['comissao']*100:.0f}% + {formatar_moeda(faixa['fixa'])}")
    c3.metric("Total descontado", formatar_moeda(taxa_reais))


def pagina_custos():
    st.header("📦 Custos de Embalagem e Custos Fixos")

    tab_emb, tab_fixo = st.tabs(["🧾 Embalagem (por peça)", "🏠 Custos Fixos Mensais"])

    # --- EMBALAGEM ---
    with tab_emb:
        st.markdown("Informe o custo unitário de cada item de embalagem utilizado por peça.")
        embalagens = st.session_state.embalagens

        with st.form("form_embalagem"):
            novos_valores = {}
            cols = st.columns(len(embalagens))
            for col, (item, valor) in zip(cols, embalagens.items()):
                novos_valores[item] = col.number_input(item, min_value=0.0, value=float(valor), step=0.05, format="%.2f")
            salvar_emb = st.form_submit_button("💾 Salvar custos de embalagem")
            if salvar_emb:
                st.session_state.embalagens.update(novos_valores)
                st.success("Custos de embalagem atualizados!")
                st.rerun()

        total_embalagem = calcular_embalagem_total()
        st.metric("Custo Total de Embalagem por Peça", formatar_moeda(total_embalagem))

    # --- CUSTOS FIXOS ---
    with tab_fixo:
        st.markdown("Cadastre as despesas fixas mensais da empresa (MEI, internet, etc).")

        # Formulário para adicionar novo custo fixo
        with st.form("form_novo_custo_fixo", clear_on_submit=True):
            c1, c2, c3 = st.columns([2, 1, 1])
            nome_custo = c1.text_input("Nome da despesa")
            valor_custo = c2.number_input("Valor mensal (R$)", min_value=0.0, step=10.0)
            adicionar = c3.form_submit_button("➕ Adicionar", use_container_width=True)
            if adicionar and nome_custo:
                st.session_state.custos_fixos.append({"nome": nome_custo, "valor": valor_custo})
                st.success(f"Despesa '{nome_custo}' adicionada!")
                st.rerun()

        # Tabela de custos fixos com opção de remover
        if st.session_state.custos_fixos:
            for i, item in enumerate(st.session_state.custos_fixos):
                c1, c2, c3 = st.columns([2, 1, 0.5])
                c1.write(item["nome"])
                c2.write(formatar_moeda(item["valor"]))
                if c3.button("🗑️", key=f"del_fixo_{i}"):
                    st.session_state.custos_fixos.pop(i)
                    st.rerun()
        else:
            st.info("Nenhuma despesa fixa cadastrada.")

        st.markdown("---")
        total_fixo = sum(item["valor"] for item in st.session_state.custos_fixos)
        qtd_produtos = len(st.session_state.produtos)
        rateio = calcular_rateio_fixo_por_peca()

        c1, c2, c3 = st.columns(3)
        c1.metric("Total de Custos Fixos", formatar_moeda(total_fixo))
        c2.metric("Produtos Cadastrados", qtd_produtos)
        c3.metric("Rateio Fixo por Peça", formatar_moeda(rateio))


def pagina_produtos():
    st.header("🛍️ Produtos e Precificação")

    # --- Formulário para adicionar novo produto ---
    with st.expander("➕ Adicionar novo produto", expanded=False):
        with st.form("form_novo_produto", clear_on_submit=True):
            c1, c2 = st.columns(2)
            codigo = c1.text_input("Código do produto")
            nome = c2.text_input("Nome do produto")
            c3, c4 = st.columns(2)
            categoria = c3.text_input("Categoria")
            custo_fab = c4.number_input("Custo de confecção/fabricação (R$)", min_value=0.0, step=0.5)
            margem = st.slider("Margem de lucro desejada (%)", min_value=1.0, max_value=90.0, value=30.0, step=0.5)

            adicionar = st.form_submit_button("Adicionar Produto", use_container_width=True)
            if adicionar:
                if codigo and nome:
                    st.session_state.produtos.append({
                        "codigo": codigo,
                        "nome": nome,
                        "categoria": categoria or "Sem categoria",
                        "custo_fabricacao": custo_fab,
                        "margem_desejada": margem,
                    })
                    st.success(f"Produto '{nome}' adicionado com sucesso!")
                    st.rerun()
                else:
                    st.warning("Preencha ao menos Código e Nome do produto.")

    st.markdown("---")

    if not st.session_state.produtos:
        st.info("Nenhum produto cadastrado ainda.")
        return

    df = montar_tabela_precificacao()

    # Formatação de exibição
    df_exibicao = df.copy()
    colunas_moeda = ["Custo Fabricação", "Embalagem", "Rateio Fixo", "Custo Total",
                      "Taxa Fixa Shopee", "Taxa Shopee (R$)", "Preço Venda Sugerido", "Lucro Líquido (R$)"]
    for col in colunas_moeda:
        df_exibicao[col] = df_exibicao[col].apply(formatar_moeda)
    df_exibicao["Margem Desejada (%)"] = df_exibicao["Margem Desejada (%)"].apply(lambda x: f"{x:.1f}%")
    df_exibicao["Comissão Shopee (%)"] = df_exibicao["Comissão Shopee (%)"].apply(lambda x: f"{x:.0f}%")
    df_exibicao["Margem Real (%)"] = df_exibicao["Margem Real (%)"].apply(lambda x: f"{x:.1f}%")

    st.subheader("📋 Tabela de Precificação")
    st.dataframe(df_exibicao, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("✏️ Editar ou Remover Produto")

    opcoes = [f"{p['codigo']} - {p['nome']}" for p in st.session_state.produtos]
    escolhido = st.selectbox("Selecione um produto:", opcoes)
    idx = opcoes.index(escolhido)
    produto_atual = st.session_state.produtos[idx]

    with st.form("form_editar_produto"):
        c1, c2 = st.columns(2)
        codigo_edit = c1.text_input("Código", value=produto_atual["codigo"])
        nome_edit = c2.text_input("Nome", value=produto_atual["nome"])
        c3, c4 = st.columns(2)
        categoria_edit = c3.text_input("Categoria", value=produto_atual["categoria"])
        custo_edit = c4.number_input("Custo de fabricação (R$)", min_value=0.0,
                                      value=float(produto_atual["custo_fabricacao"]), step=0.5)
        margem_edit = st.slider("Margem de lucro desejada (%)", min_value=1.0, max_value=90.0,
                                 value=float(produto_atual["margem_desejada"]), step=0.5)

        col_salvar, col_remover = st.columns(2)
        salvar = col_salvar.form_submit_button("💾 Salvar Alterações", use_container_width=True)
        remover = col_remover.form_submit_button("🗑️ Remover Produto", use_container_width=True)

        if salvar:
            st.session_state.produtos[idx] = {
                "codigo": codigo_edit, "nome": nome_edit, "categoria": categoria_edit,
                "custo_fabricacao": custo_edit, "margem_desejada": margem_edit,
            }
            st.success("Produto atualizado!")
            st.rerun()

        if remover:
            st.session_state.produtos.pop(idx)
            st.success("Produto removido!")
            st.rerun()


def pagina_simulador():
    st.header("🧮 Simulador de Preço")
    st.markdown("Digite um preço de venda de teste para qualquer peça e veja instantaneamente o resultado.")

    if not st.session_state.produtos:
        st.info("Cadastre ao menos um produto na aba **Produtos** para usar o simulador.")
        return

    opcoes = [f"{p['codigo']} - {p['nome']}" for p in st.session_state.produtos]
    escolhido = st.selectbox("Selecione o produto:", opcoes)
    idx = opcoes.index(escolhido)
    produto = st.session_state.produtos[idx]

    embalagem_unit = calcular_embalagem_total()
    rateio_fixo = calcular_rateio_fixo_por_peca()
    custo_total = produto["custo_fabricacao"] + embalagem_unit + rateio_fixo

    st.markdown("---")
    c1, c2 = st.columns([1, 1])
    with c1:
        st.info(
            f"**Custo Total desta peça:** {formatar_moeda(custo_total)}\n\n"
            f"(Fabricação {formatar_moeda(produto['custo_fabricacao'])} + "
            f"Embalagem {formatar_moeda(embalagem_unit)} + "
            f"Rateio Fixo {formatar_moeda(rateio_fixo)})"
        )
        preco_simulado = st.number_input(
            "💵 Digite o preço de venda de teste (R$):",
            min_value=0.0, step=1.0, value=99.90, format="%.2f",
        )

    faixa = obter_faixa_shopee(preco_simulado)
    taxa_shopee_reais = calcular_taxa_shopee_reais(preco_simulado)
    lucro_liquido = preco_simulado - custo_total - taxa_shopee_reais
    margem_real = (lucro_liquido / preco_simulado * 100) if preco_simulado > 0 else 0

    with c2:
        st.markdown(f"**Faixa de comissão aplicada:** {faixa['label']} "
                     f"({faixa['comissao']*100:.0f}% + {formatar_moeda(faixa['fixa'])})")

        m1, m2 = st.columns(2)
        m1.metric("Taxa Shopee Descontada", formatar_moeda(taxa_shopee_reais))
        m2.metric("Custo Total", formatar_moeda(custo_total))

        m3, m4 = st.columns(2)
        m3.metric("🟧 Lucro Líquido", formatar_moeda(lucro_liquido))
        m4.metric("Margem Real", f"{margem_real:.1f}%")

        if lucro_liquido < 0:
            st.error("⚠️ Atenção: com este preço a peça está dando PREJUÍZO!")
        elif margem_real < 10:
            st.warning("⚠️ Margem real abaixo de 10%. Considere revisar o preço.")
        else:
            st.success("✅ Preço saudável para esta peça.")

    # Gráfico de composição do preço simulado
    st.markdown("---")
    st.subheader("Composição do Preço Simulado")
    fig = go.Figure(data=[go.Pie(
        labels=["Custo Total", "Taxa Shopee", "Lucro Líquido"],
        values=[custo_total, taxa_shopee_reais, max(lucro_liquido, 0)],
        marker_colors=[COR_PRETO, "#8C8C8C", COR_LARANJA],
        hole=0.45,
    )])
    fig.update_layout(paper_bgcolor=COR_BRANCO, font_color=COR_PRETO)
    st.plotly_chart(fig, use_container_width=True)


# ==============================================================================
# 6. APLICAÇÃO PRINCIPAL
# ==============================================================================

def painel_principal():
    # Cabeçalho de marca
    st.markdown(
        f"""
        <div class="alpha-header">
            <h1>🧵 ALPHA <span>TÊXTIL</span></h1>
            <p>Gerenciador de Precificação — Vendas Shopee</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Sidebar com informações e logout
    with st.sidebar:
        st.markdown("## 🧵 ALPHA TÊXTIL")
        st.markdown("Painel administrativo")
        st.markdown("---")
        st.markdown(f"**Produtos cadastrados:** {len(st.session_state.produtos)}")
        st.markdown("---")
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.autenticado = False
            st.rerun()

    abas = st.tabs([
        "📊 Dashboard",
        "⚙️ Taxas Shopee",
        "📦 Custos",
        "🛍️ Produtos",
        "🧮 Simulador",
    ])

    with abas[0]:
        pagina_dashboard()
    with abas[1]:
        pagina_taxas_shopee()
    with abas[2]:
        pagina_custos()
    with abas[3]:
        pagina_produtos()
    with abas[4]:
        pagina_simulador()


def main():
    inicializar_estado()
    if not st.session_state.autenticado:
        tela_login()
    else:
        painel_principal()


if __name__ == "__main__":
    main()
