# -*- coding: utf-8 -*-
"""
================================================================================
 ESTILO.PY — Identidade visual da Manuz
================================================================================
Centraliza toda a paleta de cores e o CSS customizado da marca.
Preto absoluto predominante + Laranja vivo para destaques/lucros.
Nenhum tom de azul é utilizado em nenhum componente.
================================================================================
"""

import streamlit as st

# ------------------------------------------------------------------------------
# PALETA OFICIAL DA MARCA MANUZ
# ------------------------------------------------------------------------------
PRETO = "#000000"
PRETO_SUAVE = "#1A1A1A"
LARANJA = "#FF6600"
LARANJA_ESCURO = "#CC5200"
LARANJA_CLARO = "#FFA366"
CINZA_FUNDO = "#F4F4F4"
CINZA_CARD = "#FFFFFF"
CINZA_BORDA = "#E0E0E0"
CINZA_TEXTO = "#333333"
VERDE_OK = "#2E7D32"
AMARELO_ATENCAO = "#B8860B"
VERMELHO_RISCO = "#C0392B"

# Sequência de cores usada em todos os gráficos Plotly (sem azul)
PALETA_GRAFICO = [LARANJA, PRETO, LARANJA_CLARO, "#595959", "#FF8C33", "#8C8C8C"]


def aplicar_estilo():
    """Injeta o CSS global da marca Manuz na aplicação Streamlit."""
    st.markdown(
        f"""
        <style>
            .stApp {{ background-color: {CINZA_FUNDO}; }}

            h1, h2, h3 {{ color: {PRETO} !important; font-weight: 800 !important; }}

            section[data-testid="stSidebar"] {{ background-color: {PRETO}; }}
            section[data-testid="stSidebar"] * {{ color: {CINZA_FUNDO} !important; }}
            section[data-testid="stSidebar"] .stButton button {{
                background-color: {LARANJA}; color: {PRETO} !important;
                border: none; font-weight: 700;
            }}

            .stButton button {{
                background-color: {LARANJA}; color: {PRETO};
                font-weight: 700; border: none; border-radius: 6px;
                transition: 0.2s;
            }}
            .stButton button:hover {{ background-color: {LARANJA_ESCURO}; color: {CINZA_FUNDO}; }}

            .stTabs [data-baseweb="tab-list"] {{ gap: 6px; }}
            .stTabs [data-baseweb="tab"] {{
                background-color: {CINZA_CARD}; border-radius: 6px 6px 0 0;
                padding: 8px 16px; border: 1px solid {CINZA_BORDA};
            }}
            .stTabs [aria-selected="true"] {{
                background-color: {PRETO} !important; color: {LARANJA} !important;
            }}

            div[data-testid="stMetric"] {{
                background-color: {CINZA_CARD}; border: 1px solid {CINZA_BORDA};
                border-left: 6px solid {LARANJA}; border-radius: 8px;
                padding: 14px 18px; box-shadow: 0 1px 4px rgba(0,0,0,0.08);
            }}
            div[data-testid="stMetricValue"] {{ color: {PRETO} !important; font-weight: 800 !important; }}
            div[data-testid="stMetricLabel"] {{ color: {CINZA_TEXTO} !important; }}

            .stDataFrame {{ border: 1px solid {CINZA_BORDA}; border-radius: 6px; }}
            hr {{ border-top: 2px solid {LARANJA}; }}

            .manuz-header {{
                background-color: {PRETO}; padding: 18px 24px; border-radius: 8px;
                margin-bottom: 18px; border-left: 8px solid {LARANJA};
            }}
            .manuz-header h1 {{ color: {CINZA_FUNDO} !important; margin: 0; font-size: 28px; }}
            .manuz-header span {{ color: {LARANJA}; }}
            .manuz-header p {{ color: #cccccc; margin: 0; font-size: 14px; }}

            .badge-perfil {{
                display: inline-block; background-color: {LARANJA}; color: {PRETO};
                padding: 3px 12px; border-radius: 20px; font-weight: 700; font-size: 12px;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def formatar_moeda(valor: float) -> str:
    """Formata um valor float para o padrão monetário brasileiro (R$ 1.234,56)."""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
